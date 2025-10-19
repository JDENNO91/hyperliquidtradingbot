"""
Simple Risk Manager

A simplified risk management system that focuses on basic position sizing
without complex tracking that can cause issues.
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class RiskMetrics:
    """Simple risk metrics."""
    max_drawdown: float = 0.0
    current_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    max_position_size: float = 0.0
    total_exposure: float = 0.0
    margin_utilization: float = 0.0
    consecutive_losses: int = 0
    max_consecutive_losses: int = 5

class SimpleRiskManager:
    """
    Simple risk manager with basic position sizing and risk controls.
    
    This manager provides:
    - Basic position sizing
    - Simple risk checks
    - Minimal tracking to avoid complexity issues
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the simple risk manager.
        
        Args:
            config: Risk management configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Basic risk parameters
        self.max_risk_per_trade = config.get('max_risk_per_trade', 0.02)  # 2% per trade
        self.max_position_size = config.get('max_position_size', 0.1)     # 10% max position
        self.max_open_positions = config.get('max_open_positions', 5)     # Max concurrent positions
        self.max_drawdown = config.get('max_drawdown', 0.25)             # 25% max drawdown
        
        # Simple tracking
        self.initial_capital = config.get('initial_capital', 10000)
        self.current_capital = self.initial_capital
        self.open_positions_count = 0
        
        self.logger.info(f"Simple risk manager initialized with max risk per trade: {self.max_risk_per_trade:.1%}")
    
    def can_open_position(self, direction: str, strength: float, price: float, current_position_count: int) -> bool:
        """
        Check if a new position can be opened.
        
        Args:
            direction: Position direction ('LONG' or 'SHORT')
            strength: Signal strength (0.0 to 1.0)
            price: Entry price
            current_position_count: Current number of open positions
            
        Returns:
            True if position can be opened
        """
        # Check position count limit
        if current_position_count >= self.max_open_positions:
            self.logger.debug(f"Cannot open position: max positions ({self.max_open_positions}) reached")
            return False
        
        # Check if we have enough capital
        if self.current_capital <= 0:
            self.logger.debug("Cannot open position: no capital available")
            return False
        
        return True
    
    def calculate_position_size(self, capital: float, entry_price: float, stop_loss: float) -> float:
        """
        Calculate position size based on risk per trade.
        
        Args:
            capital: Available capital
            entry_price: Entry price
            stop_loss: Stop loss price
            
        Returns:
            Position size
        """
        if capital <= 0 or entry_price <= 0:
            return 0.0
        
        # FIX: Use INITIAL capital for position sizing to prevent exponential growth
        # This ensures position sizes don't compound based on profits
        sizing_capital = self.initial_capital
        
        # Calculate risk amount
        risk_amount = sizing_capital * self.max_risk_per_trade
        
        # Calculate price risk (percentage)
        price_risk_pct = abs(entry_price - stop_loss) / entry_price if stop_loss > 0 else 0.01
        
        # SAFETY: Ensure minimum price risk to prevent huge position sizes
        # If stop loss is very tight (< 0.5%), use 0.5% minimum
        if price_risk_pct < 0.005:
            self.logger.debug(f"Price risk too tight ({price_risk_pct:.4%}), using 0.5% minimum")
            price_risk_pct = 0.005
        
        # Calculate position value we can afford given the risk
        # If we risk 2% of capital on a 1% price move, we can have 2% / 1% = 2x capital position
        # But we cap this to max_position_size
        position_value_limit = sizing_capital * min(self.max_risk_per_trade / price_risk_pct, self.max_position_size)
        
        # Convert to position size (number of units)
        position_size = position_value_limit / entry_price
        
        # ABSOLUTE CAP: Never more than 20% of capital in a single position
        # This prevents crazy position sizes even with very tight stops
        absolute_max_value = sizing_capital * 0.2
        absolute_max_size = absolute_max_value / entry_price
        position_size = min(position_size, absolute_max_size)
        
        self.logger.debug(f"Position size: {position_size:.4f} (value: ${position_size * entry_price:.2f}, risk%: {price_risk_pct:.2%})")
        
        return position_size
    
    def open_position_from_object(self, position) -> bool:
        """
        Track opening a position from a position object.
        
        Args:
            position: Position object
            
        Returns:
            True if successful
        """
        self.open_positions_count += 1
        self.logger.debug(f"Position opened: {position.id} (total open: {self.open_positions_count})")
        return True
    
    def close_position(self, position_id: str, exit_price: float = 0.0, exit_time: str = "") -> bool:
        """
        Track closing a position.
        
        Args:
            position_id: Position ID
            exit_price: Exit price (optional)
            exit_time: Exit time (optional)
            
        Returns:
            True if successful
        """
        if self.open_positions_count > 0:
            self.open_positions_count -= 1
        
        self.logger.debug(f"Position closed: {position_id} (total open: {self.open_positions_count})")
        return True
    
    def get_risk_metrics(self) -> RiskMetrics:
        """
        Get current risk metrics.
        
        Returns:
            Risk metrics object
        """
        return RiskMetrics(
            max_drawdown=0.0,
            current_drawdown=0.0,
            sharpe_ratio=0.0,
            max_position_size=self.max_position_size,
            total_exposure=self.open_positions_count * self.max_position_size,
            margin_utilization=0.0,
            consecutive_losses=0,
            max_consecutive_losses=5
        )
    
    def reset(self) -> None:
        """Reset the risk manager."""
        self.current_capital = self.initial_capital
        self.open_positions_count = 0
        self.logger.info("Simple risk manager reset")
    
    def __str__(self) -> str:
        """String representation of the risk manager."""
        return f"SimpleRiskManager(open: {self.open_positions_count}, capital: {self.current_capital:.2f})"
    
    def __repr__(self) -> str:
        """Detailed representation of the risk manager."""
        return self.__str__()
