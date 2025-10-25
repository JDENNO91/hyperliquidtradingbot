"""
Base Strategy Class

This abstract base class defines the interface that all trading strategies must implement.
It provides common functionality and enforces consistent behavior across different strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging

@dataclass
class Signal:
    """Represents a trading signal with direction and strength."""
    direction: str  # 'LONG', 'SHORT', 'CLOSE_LONG', 'CLOSE_SHORT', 'NONE'
    strength: float  # Signal strength (0.0 to 1.0)
    reason: str  # Human-readable reason for the signal
    metadata: Dict[str, Any]  # Additional signal information
    price: float = 0.0  # Current price when signal was generated
    symbol: str = ''  # Trading symbol
    timestamp: float = 0.0  # Timestamp when signal was generated
    stop_loss: float = 0.0  # Stop loss price for the signal

@dataclass
class Position:
    """Represents a trading position."""
    id: str  # Unique position identifier
    symbol: str  # Trading symbol
    side: str  # 'LONG' or 'SHORT'
    entry_price: float
    entry_time: str
    exit_price: float = 0.0  # Exit price (0.0 if not closed)
    exit_time: str = ""  # Exit time (empty if not closed)
    size: float = 0.0
    notional: float = 0.0
    status: str = "OPEN"  # 'OPEN', 'CLOSED', 'CANCELLED'
    pnl: float = 0.0  # Profit/Loss
    stop_loss: float = 0.0  # Stop loss price
    metadata: Dict[str, Any] = None  # Additional position information
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    
    This class defines the interface and common functionality that all strategies
    must implement. It provides:
    - Signal generation interface
    - Position management
    - Risk management integration
    - Performance tracking
    - Configuration management
    """
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        Initialize the strategy with configuration and logger.
        
        Args:
            config: Strategy configuration dictionary
            logger: Logger instance for strategy logging
        """
        self.config = config
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.name = self.__class__.__name__
        self.market = config.get('trading', {}).get('market', 'UNKNOWN')
        self.timeframe = config.get('trading', {}).get('timeframe', '1m')
        
        # Performance tracking
        self.total_signals = 0
        self.successful_signals = 0
        self.failed_signals = 0
        
        # Position tracking
        self.current_position: Optional[Position] = None
        self.position_history: list[Position] = []
        
        self.logger.info(f"Initialized {self.name} strategy for {self.market} on {self.timeframe}")
    
    @abstractmethod
    def compute_indicators(self, data: list[Dict[str, Any]], index: int) -> Dict[str, Any]:
        """
        Compute technical indicators for the given data point.
        
        Args:
            data: Historical market data
            index: Current data index
            
        Returns:
            Dictionary containing computed indicators
        """
        pass
    
    @abstractmethod
    def generate_signal(self, data: list[Dict[str, Any]], index: int) -> Signal:
        """
        Generate a trading signal based on current market conditions.
        
        Args:
            data: Historical market data
            index: Current data index
            
        Returns:
            Signal object indicating trading action
        """
        pass
    
    def evaluate_position(self, data: list[Dict[str, Any]], index: int) -> Signal:
        """
        Evaluate current position and determine if it should be closed.
        
        Args:
            data: Historical market data
            index: Current data index
            
        Returns:
            Signal object for position management
        """
        if not self.current_position:
            return Signal('NONE', 0.0, 'No position to evaluate', {}, 0.0, '', 0.0)
        
        # Default implementation - can be overridden by subclasses
        return self._default_exit_logic(data, index)
    
    def _default_exit_logic(self, data: list[Dict[str, Any]], index: int) -> Signal:
        """
        Default exit logic based on basic risk management.
        
        Args:
            data: Historical market data
            index: Current data index
            
        Returns:
            Signal object for exit decision
        """
        if not self.current_position:
            return Signal('NONE', 0.0, 'No position to evaluate', {}, 0.0, '', 0.0)
        
        current_price = data[index]['close']
        entry_price = self.current_position.entry_price
        
        # Simple take-profit and stop-loss logic
        take_profit_pct = self.config.get('trading', {}).get('take_profit_pct', 0.03)
        stop_loss_pct = self.config.get('trading', {}).get('stop_loss_pct', 0.015)
        
        if self.current_position.side == 'LONG':
            profit_pct = (current_price - entry_price) / entry_price
            if profit_pct >= take_profit_pct:
                return Signal('CLOSE_LONG', 1.0, f'Take profit reached: {profit_pct:.2%}', {}, current_price, '', 0.0)
            elif profit_pct <= -stop_loss_pct:
                return Signal('CLOSE_LONG', 1.0, f'Stop loss triggered: {profit_pct:.2%}', {}, current_price, '', 0.0)
        
        elif self.current_position.side == 'SHORT':
            profit_pct = (entry_price - current_price) / entry_price
            if profit_pct >= take_profit_pct:
                return Signal('CLOSE_SHORT', 1.0, f'Take profit reached: {profit_pct:.2%}', {}, current_price, '', 0.0)
            elif profit_pct <= -stop_loss_pct:
                return Signal('CLOSE_SHORT', 1.0, f'Stop loss triggered: {profit_pct:.2%}', {}, current_price, '', 0.0)
        
        return Signal('NONE', 0.0, 'Position held', {}, 0.0, '', 0.0)
    
    def update_position(self, position: Optional[Position]):
        """
        Update the current position.
        
        Args:
            position: New position or None to clear position
        """
        if self.current_position:
            self.position_history.append(self.current_position)
        
        self.current_position = position
        
        if position:
            self.logger.info(f"Position updated: {position.side} {position.size} @ {position.entry_price}")
        else:
            self.logger.info("Position cleared")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get strategy performance statistics.
        
        Returns:
            Dictionary containing performance metrics
        """
        total_positions = len(self.position_history)
        if total_positions == 0:
            return {
                'total_signals': self.total_signals,
                'total_positions': 0,
                'win_rate': 0.0,
                'avg_profit': 0.0,
                'avg_loss': 0.0
            }
        
        profitable_positions = sum(1 for p in self.position_history if self._is_profitable(p))
        win_rate = profitable_positions / total_positions
        
        profits = [self._calculate_profit(p) for p in self.position_history if self._is_profitable(p)]
        losses = [self._calculate_profit(p) for p in self.position_history if not self._is_profitable(p)]
        
        avg_profit = sum(profits) / len(profits) if profits else 0.0
        avg_loss = sum(losses) / len(losses) if losses else 0.0
        
        return {
            'total_signals': self.total_signals,
            'total_positions': total_positions,
            'win_rate': win_rate,
            'avg_profit': avg_profit,
            'avg_loss': avg_loss,
            'profit_factor': abs(avg_profit / avg_loss) if avg_loss != 0 else float('inf')
        }
    
    def _is_profitable(self, position: Position) -> bool:
        """Check if a position was profitable."""
        # This is a simplified check - in practice, you'd compare entry/exit prices
        return True  # Placeholder
    
    def _calculate_profit(self, position: Position) -> float:
        """Calculate the profit/loss for a position."""
        # This is a simplified calculation - in practice, you'd use actual exit data
        return 0.0  # Placeholder
    
    def validate_config(self) -> bool:
        """
        Validate strategy configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        required_keys = ['trading', 'indicators']
        
        for key in required_keys:
            if key not in self.config:
                self.logger.error(f"Missing required config key: {key}")
                return False
        
        # Validate trading config
        trading_config = self.config['trading']
        required_trading_keys = ['market', 'positionSize', 'leverage']
        
        for key in required_trading_keys:
            if key not in trading_config:
                self.logger.error(f"Missing required trading config key: {key}")
                return False
        
        return True
    
    def __str__(self) -> str:
        return f"{self.name}(market={self.market}, timeframe={self.timeframe})"
    
    def __repr__(self) -> str:
        return self.__str__()
