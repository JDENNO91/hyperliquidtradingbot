"""
Improved Trading Engine

A robust trading engine with proper position management and signal execution.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import time

from .base_strategy import BaseStrategy, Signal
from .improved_position_manager import ImprovedPositionManager
from .simple_risk_manager import SimpleRiskManager

logger = logging.getLogger(__name__)

class ImprovedTradingEngine:
    """
    Improved trading engine with robust position management and signal execution.
    
    This engine provides:
    - Reliable signal execution
    - Proper position lifecycle management
    - Risk controls and position limits
    - Performance tracking
    - Clean error handling
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the improved trading engine.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.risk_manager = SimpleRiskManager(config.get('risk_management', {}))
        self.position_manager = ImprovedPositionManager(config.get('position_management', {}))
        
        # Strategy
        self.strategy: Optional[BaseStrategy] = None
        
        # Engine state
        self.is_running = False
        self.is_paused = False
        self.start_time: Optional[datetime] = None
        
        # Performance tracking
        self.total_signals = 0
        self.executed_signals = 0
        self.failed_signals = 0
        self.signal_history: List[Signal] = []
        
        # Market data
        self.current_market_data: Optional[Dict[str, Any]] = None
        self.market_data_history: List[Dict[str, Any]] = []
        
        # Capital management
        self.initial_capital = config.get('initial_capital', 10000.0)
        self.current_capital = self.initial_capital
        
        self.logger.info("Improved trading engine initialized")
        self.logger.info(f"Initial capital: ${self.initial_capital:,.2f}")
    
    def set_strategy(self, strategy: BaseStrategy) -> None:
        """
        Set the trading strategy.
        
        Args:
            strategy: Strategy instance
        """
        self.strategy = strategy
        self.logger.info(f"Strategy set: {strategy.__class__.__name__}")
    
    def start(self) -> None:
        """Start the trading engine."""
        if self.is_running:
            self.logger.warning("Trading engine is already running")
            return
        
        self.is_running = True
        self.is_paused = False
        self.start_time = datetime.now()
        
        self.logger.info("Trading engine started")
    
    def stop(self) -> None:
        """Stop the trading engine."""
        if not self.is_running:
            self.logger.warning("Trading engine is not running")
            return
        
        self.is_running = False
        self.is_paused = False
        
        # Close all open positions
        if self.position_manager.open_positions:
            self.logger.info("Closing all open positions before stopping")
            self.position_manager.close_all_positions(
                exit_price=self._get_current_price(),
                reason="Engine stop"
            )
        
        self.logger.info("Trading engine stopped")
    
    def pause(self) -> None:
        """Pause the trading engine."""
        if not self.is_running:
            self.logger.warning("Trading engine is not running")
            return
        
        self.is_paused = True
        self.logger.info("Trading engine paused")
    
    def resume(self) -> None:
        """Resume the trading engine."""
        if not self.is_running:
            self.logger.warning("Trading engine is not running")
            return
        
        self.is_paused = False
        self.logger.info("Trading engine resumed")
    
    def process_market_data(self, market_data: Dict[str, Any]) -> None:
        """
        Process new market data and execute strategy signals.
        
        Args:
            market_data: Market data dictionary
        """
        if not self.is_running or self.is_paused:
            return
        
        self.current_market_data = market_data
        self.market_data_history.append(market_data)
        
        # Update position P&L
        current_price = self._get_current_price()
        self.position_manager.update_position_pnl(current_price)
        
        # Check for stop loss triggers
        triggered_positions = self.position_manager.check_stop_losses(current_price)
        for position in triggered_positions:
            self.logger.info(f"Stop loss triggered for position {position.id}")
            self.position_manager.close_position(
                position.id, 
                current_price, 
                reason="Stop loss"
            )
        
        # Execute strategy if available
        if self.strategy:
            try:
                # Generate signal from strategy
                signal = self.strategy.generate_signal(self.market_data_history, len(self.market_data_history) - 1)
                
                if signal and signal.direction != 'NONE':
                    self.total_signals += 1
                    self.signal_history.append(signal)
                    
                    # Execute signal
                    success = self.execute_signal(signal)
                    if success:
                        self.executed_signals += 1
                    else:
                        self.failed_signals += 1
                
                # Check for position exit signals
                if self.position_manager.open_positions:
                    exit_signal = self.strategy.evaluate_position(self.market_data_history, len(self.market_data_history) - 1)
                    if exit_signal and exit_signal.direction in ['CLOSE_LONG', 'CLOSE_SHORT', 'CLOSE_ALL']:
                        self._handle_exit_signal(exit_signal, current_price)
                
            except Exception as e:
                self.logger.error(f"Error processing market data: {e}")
    
    def execute_signal(self, signal: Signal) -> bool:
        """
        Execute a trading signal.
        
        Args:
            signal: Signal to execute
            
        Returns:
            True if executed successfully
        """
        try:
            if signal.direction in ['LONG', 'SHORT']:
                return self._execute_entry_signal(signal)
            elif signal.direction in ['CLOSE_LONG', 'CLOSE_SHORT', 'CLOSE_ALL']:
                return self._execute_exit_signal(signal)
            else:
                self.logger.warning(f"Unknown signal direction: {signal.direction}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error executing signal: {e}")
            return False
    
    def _execute_entry_signal(self, signal: Signal) -> bool:
        """
        Execute an entry signal.
        
        Args:
            signal: Entry signal
            
        Returns:
            True if executed successfully
        """
        try:
            # Check if we can open a position
            can_open, reason = self.position_manager.can_open_position(signal.symbol, signal.direction)
            if not can_open:
                self.logger.info(f"Cannot open position: {reason}")
                return False
            
            # Check risk limits
            if not self.risk_manager.can_open_position(signal.direction, signal.strength, signal.price, len(self.position_manager.open_positions)):
                self.logger.info("Cannot open position: risk limits exceeded")
                return False
            
            # Calculate position size
            position_size = self.risk_manager.calculate_position_size(
                self.current_capital,
                signal.price,
                signal.stop_loss
            )
            
            # Open position
            position = self.position_manager.open_position(
                symbol=signal.symbol,
                side=signal.direction,
                entry_price=signal.price,
                size=position_size,
                timestamp=signal.timestamp,
                stop_loss=signal.stop_loss,
                metadata={
                    'signal_strength': signal.strength,
                    'signal_reason': signal.reason,
                    'signal_metadata': signal.metadata
                }
            )
            
            # Update risk manager
            self.risk_manager.open_position_from_object(position)
            
            self.logger.info(f"Position opened: {position.id} - {signal.direction} {signal.symbol} @ {signal.price}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error executing entry signal: {e}")
            return False
    
    def _execute_exit_signal(self, signal: Signal) -> bool:
        """
        Execute an exit signal.
        
        Args:
            signal: Exit signal
            
        Returns:
            True if executed successfully
        """
        try:
            current_price = self._get_current_price()
            closed_positions = []
            
            if signal.direction == 'CLOSE_ALL':
                closed_positions = self.position_manager.close_all_positions(
                    exit_price=current_price,
                    reason=signal.reason
                )
            elif signal.direction == 'CLOSE_LONG':
                long_positions = [p for p in self.position_manager.open_positions.values() if p.side == 'LONG']
                for position in long_positions:
                    closed = self.position_manager.close_position(
                        position.id, 
                        current_price, 
                        reason=signal.reason
                    )
                    if closed:
                        closed_positions.append(closed)
            elif signal.direction == 'CLOSE_SHORT':
                short_positions = [p for p in self.position_manager.open_positions.values() if p.side == 'SHORT']
                for position in short_positions:
                    closed = self.position_manager.close_position(
                        position.id, 
                        current_price, 
                        reason=signal.reason
                    )
                    if closed:
                        closed_positions.append(closed)
            
            # Update risk manager
            for position in closed_positions:
                self.risk_manager.close_position(position.id)
            
            if closed_positions:
                self.logger.info(f"Closed {len(closed_positions)} positions: {signal.reason}")
                return True
            else:
                self.logger.info(f"No positions to close for signal: {signal.reason}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error executing exit signal: {e}")
            return False
    
    def _handle_exit_signal(self, exit_signal: Signal, current_price: float) -> None:
        """
        Handle position exit signals from strategy.
        
        Args:
            exit_signal: Exit signal from strategy
            current_price: Current market price
        """
        try:
            if exit_signal.direction == 'CLOSE_ALL':
                self.position_manager.close_all_positions(
                    exit_price=current_price,
                    reason=exit_signal.reason
                )
            elif exit_signal.direction == 'CLOSE_LONG':
                long_positions = [p for p in self.position_manager.open_positions.values() if p.side == 'LONG']
                for position in long_positions:
                    self.position_manager.close_position(
                        position.id, 
                        current_price, 
                        reason=exit_signal.reason
                    )
            elif exit_signal.direction == 'CLOSE_SHORT':
                short_positions = [p for p in self.position_manager.open_positions.values() if p.side == 'SHORT']
                for position in short_positions:
                    self.position_manager.close_position(
                        position.id, 
                        current_price, 
                        reason=exit_signal.reason
                    )
        except Exception as e:
            self.logger.error(f"Error handling exit signal: {e}")
    
    def _get_current_price(self) -> float:
        """
        Get current market price from market data.
        
        Returns:
            Current price or 0.0 if not available
        """
        if not self.current_market_data:
            return 0.0
        
        # Try different price fields
        price_fields = ['close', 'c', 'price', 'last']
        for field in price_fields:
            if field in self.current_market_data:
                return float(self.current_market_data[field])
        
        return 0.0
    
    def get_engine_status(self) -> Dict[str, Any]:
        """
        Get current engine status.
        
        Returns:
            Dictionary containing engine status information
        """
        uptime = 0.0
        if self.start_time:
            uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'uptime_seconds': uptime,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'current_capital': self.current_capital,
            'total_pnl': self.position_manager.total_pnl,
            'open_positions': len(self.position_manager.open_positions),
            'closed_positions': len(self.position_manager.closed_positions)
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive performance statistics.
        
        Returns:
            Dictionary containing performance metrics
        """
        engine_status = self.get_engine_status()
        position_stats = self.position_manager.get_position_statistics()
        
        return {
            'engine_status': engine_status,
            'signal_stats': {
                'total_signals': self.total_signals,
                'executed_signals': self.executed_signals,
                'failed_signals': self.failed_signals,
                'success_rate': (self.executed_signals / max(self.total_signals, 1)) * 100
            },
            'position_stats': position_stats,
            'capital_stats': {
                'initial_capital': self.initial_capital,
                'current_capital': self.current_capital,
                'total_pnl': self.position_manager.total_pnl,
                'return_percentage': (self.position_manager.total_pnl / self.initial_capital) * 100
            }
        }
    
    def reset(self) -> None:
        """Reset the trading engine."""
        self.stop()
        self.position_manager.reset()
        self.risk_manager.reset()
        
        self.total_signals = 0
        self.executed_signals = 0
        self.failed_signals = 0
        self.signal_history.clear()
        self.market_data_history.clear()
        self.current_capital = self.initial_capital
        
        self.logger.info("Trading engine reset")
    
    def __str__(self) -> str:
        """String representation of the trading engine."""
        status = "RUNNING" if self.is_running else "STOPPED"
        if self.is_paused:
            status += " (PAUSED)"
        
        return f"TradingEngine(status={status}, positions={len(self.position_manager.open_positions)})"
    
    def __repr__(self) -> str:
        """Detailed representation of the trading engine."""
        return self.__str__()
