"""
Improved Position Manager

A robust position management system that properly tracks positions and handles
position lifecycle management for backtesting and live trading.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import time
import uuid

from .base_strategy import Position

logger = logging.getLogger(__name__)

class ImprovedPositionManager:
    """
    Improved position manager with robust tracking and lifecycle management.
    
    This manager provides:
    - Reliable position tracking with unique IDs
    - Proper position lifecycle management
    - Risk controls and position limits
    - Performance tracking and statistics
    - Clean position closing and cleanup
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the improved position manager.
        
        Args:
            config: Position management configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Position tracking
        self.positions: Dict[str, Position] = {}  # All positions by ID
        self.open_positions: Dict[str, Position] = {}  # Currently open positions
        self.closed_positions: List[Position] = []  # Closed positions for history
        
        # Position limits and controls
        self.max_concurrent_positions = config.get('max_concurrent_positions', 1)
        self.max_position_size = config.get('max_position_size', 0.1)  # 10% of capital
        self.allow_multiple_symbols = config.get('allow_multiple_symbols', False)
        self.allow_hedging = config.get('allow_hedging', False)  # Allow LONG and SHORT simultaneously
        
        # Risk controls
        self.max_drawdown_per_position = config.get('max_drawdown_per_position', 0.05)  # 5%
        self.auto_close_on_max_loss = config.get('auto_close_on_max_loss', True)
        
        # Statistics
        self.total_positions_opened = 0
        self.total_positions_closed = 0
        self.total_pnl = 0.0
        
        self.logger.info(f"Improved position manager initialized:")
        self.logger.info(f"  - Max concurrent positions: {self.max_concurrent_positions}")
        self.logger.info(f"  - Max position size: {self.max_position_size:.1%}")
        self.logger.info(f"  - Allow multiple symbols: {self.allow_multiple_symbols}")
        self.logger.info(f"  - Allow hedging: {self.allow_hedging}")
    
    def can_open_position(self, symbol: str, side: str) -> Tuple[bool, str]:
        """
        Check if a new position can be opened.
        
        Args:
            symbol: Trading symbol
            side: Position side ('LONG' or 'SHORT')
            
        Returns:
            Tuple of (can_open, reason)
        """
        # Check concurrent position limit
        if len(self.open_positions) >= self.max_concurrent_positions:
            return False, f"Maximum concurrent positions ({self.max_concurrent_positions}) reached"
        
        # Check if we already have a position in this symbol
        existing_positions = [p for p in self.open_positions.values() if p.symbol == symbol]
        
        if existing_positions and not self.allow_hedging:
            return False, f"Position already exists for {symbol}"
        
        # Check hedging rules
        if existing_positions and not self.allow_hedging:
            existing_side = existing_positions[0].side
            if existing_side != side:
                return False, f"Cannot hedge {symbol}: existing {existing_side}, trying to open {side}"
        
        return True, "OK"
    
    def open_position(self, symbol: str, side: str, entry_price: float, 
                     size: float, timestamp: Optional[float] = None,
                     stop_loss: Optional[float] = None, metadata: Optional[Dict[str, Any]] = None) -> Position:
        """
        Open a new trading position.
        
        Args:
            symbol: Trading symbol
            side: Position side ('LONG' or 'SHORT')
            entry_price: Entry price
            size: Position size
            timestamp: Entry timestamp
            stop_loss: Stop loss price
            metadata: Additional position metadata
            
        Returns:
            Created position object
            
        Raises:
            RuntimeError: If position cannot be opened
        """
        # Check if position can be opened
        can_open, reason = self.can_open_position(symbol, side)
        if not can_open:
            raise RuntimeError(f"Cannot open position: {reason}")
        
        if timestamp is None:
            timestamp = time.time()
        
        if metadata is None:
            metadata = {}
        
        # Generate unique position ID
        position_id = f"pos_{uuid.uuid4().hex[:8]}_{int(timestamp)}"
        
        # Create new position
        position = Position(
            id=position_id,
            symbol=symbol,
            side=side,
            entry_price=entry_price,
            entry_time=str(timestamp),
            size=size,
            notional=entry_price * size,
            stop_loss=stop_loss or 0.0,
            metadata=metadata
        )
        
        # Add to tracking dictionaries
        self.positions[position_id] = position
        self.open_positions[position_id] = position
        
        # Update statistics
        self.total_positions_opened += 1
        
        self.logger.info(f"Position opened: {position_id} - {side} {symbol} @ {entry_price} (size: {size})")
        self.logger.debug(f"Open positions: {len(self.open_positions)}/{self.max_concurrent_positions}")
        
        return position
    
    def close_position(self, position_id: str, exit_price: float, 
                      exit_time: Optional[float] = None, reason: str = "Manual") -> Optional[Position]:
        """
        Close a position by ID.
        
        Args:
            position_id: Position ID to close
            exit_price: Exit price
            exit_time: Exit timestamp
            reason: Reason for closing
            
        Returns:
            Closed position object or None if not found
        """
        if position_id not in self.open_positions:
            self.logger.warning(f"Position {position_id} not found for closing")
            return None
        
        if exit_time is None:
            exit_time = time.time()
        
        position = self.open_positions[position_id]
        
        # Calculate P&L
        if position.side == 'LONG':
            pnl = (exit_price - position.entry_price) * position.size
        else:  # SHORT
            pnl = (position.entry_price - exit_price) * position.size
        
        # SAFETY CHECK: Cap P&L to prevent astronomical values
        # A single trade should never make more than 10x the initial position value
        max_reasonable_pnl = position.notional * 10
        if abs(pnl) > max_reasonable_pnl:
            self.logger.warning(f"P&L capped: {pnl:.2f} -> {max_reasonable_pnl if pnl > 0 else -max_reasonable_pnl:.2f}")
            pnl = max_reasonable_pnl if pnl > 0 else -max_reasonable_pnl
        
        # Update position
        position.exit_price = exit_price
        position.exit_time = str(exit_time)
        position.status = "CLOSED"
        position.pnl = pnl
        position.metadata['close_reason'] = reason
        
        # Move from open to closed
        del self.open_positions[position_id]
        self.closed_positions.append(position)
        
        # Update statistics
        self.total_positions_closed += 1
        self.total_pnl += pnl
        
        self.logger.info(f"Position closed: {position_id} - {position.side} {position.symbol} @ {exit_price} (PnL: {pnl:.2f})")
        self.logger.debug(f"Open positions: {len(self.open_positions)}/{self.max_concurrent_positions}")
        
        return position
    
    def close_position_by_symbol(self, symbol: str, exit_price: float, 
                                exit_time: Optional[float] = None, reason: str = "Manual") -> List[Position]:
        """
        Close all positions for a specific symbol.
        
        Args:
            symbol: Symbol to close positions for
            exit_price: Exit price
            exit_time: Exit timestamp
            reason: Reason for closing
            
        Returns:
            List of closed positions
        """
        positions_to_close = [p for p in self.open_positions.values() if p.symbol == symbol]
        closed_positions = []
        
        for position in positions_to_close:
            closed = self.close_position(position.id, exit_price, exit_time, reason)
            if closed:
                closed_positions.append(closed)
        
        return closed_positions
    
    def close_all_positions(self, exit_price: float, exit_time: Optional[float] = None, 
                           reason: str = "Manual") -> List[Position]:
        """
        Close all open positions.
        
        Args:
            exit_price: Exit price (will be used for all positions)
            exit_time: Exit timestamp
            reason: Reason for closing
            
        Returns:
            List of closed positions
        """
        positions_to_close = list(self.open_positions.values())
        closed_positions = []
        
        for position in positions_to_close:
            closed = self.close_position(position.id, exit_price, exit_time, reason)
            if closed:
                closed_positions.append(closed)
        
        return closed_positions
    
    def get_position(self, position_id: str) -> Optional[Position]:
        """
        Get a position by ID.
        
        Args:
            position_id: Position ID
            
        Returns:
            Position object or None if not found
        """
        return self.positions.get(position_id)
    
    def get_open_positions(self, symbol: Optional[str] = None) -> List[Position]:
        """
        Get all open positions, optionally filtered by symbol.
        
        Args:
            symbol: Optional symbol filter
            
        Returns:
            List of open positions
        """
        if symbol is None:
            return list(self.open_positions.values())
        else:
            return [p for p in self.open_positions.values() if p.symbol == symbol]
    
    def get_closed_positions(self, symbol: Optional[str] = None) -> List[Position]:
        """
        Get all closed positions, optionally filtered by symbol.
        
        Args:
            symbol: Optional symbol filter
            
        Returns:
            List of closed positions
        """
        if symbol is None:
            return self.closed_positions.copy()
        else:
            return [p for p in self.closed_positions if p.symbol == symbol]
    
    def update_position_pnl(self, current_price: float) -> None:
        """
        Update unrealized P&L for all open positions.
        
        Args:
            current_price: Current market price
        """
        for position in self.open_positions.values():
            if position.side == 'LONG':
                unrealized_pnl = (current_price - position.entry_price) * position.size
            else:  # SHORT
                unrealized_pnl = (position.entry_price - current_price) * position.size
            
            position.metadata['unrealized_pnl'] = unrealized_pnl
    
    def check_stop_losses(self, current_price: float) -> List[Position]:
        """
        Check for stop loss triggers and return positions that should be closed.
        
        Args:
            current_price: Current market price
            
        Returns:
            List of positions that hit stop loss
        """
        triggered_positions = []
        
        for position in self.open_positions.values():
            if position.stop_loss <= 0:
                continue
            
            should_trigger = False
            
            if position.side == 'LONG' and current_price <= position.stop_loss:
                should_trigger = True
            elif position.side == 'SHORT' and current_price >= position.stop_loss:
                should_trigger = True
            
            if should_trigger:
                triggered_positions.append(position)
        
        return triggered_positions
    
    def get_position_statistics(self) -> Dict[str, Any]:
        """
        Get position management statistics.
        
        Returns:
            Dictionary containing position statistics
        """
        total_trades = len(self.closed_positions)
        winning_trades = len([p for p in self.closed_positions if p.pnl > 0])
        losing_trades = len([p for p in self.closed_positions if p.pnl < 0])
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0
        
        avg_win = sum(p.pnl for p in self.closed_positions if p.pnl > 0) / max(winning_trades, 1)
        avg_loss = sum(p.pnl for p in self.closed_positions if p.pnl < 0) / max(losing_trades, 1)
        
        return {
            'total_positions_opened': self.total_positions_opened,
            'total_positions_closed': self.total_positions_closed,
            'current_open_positions': len(self.open_positions),
            'total_pnl': self.total_pnl,
            'win_rate': win_rate,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'breakeven_trades': total_trades - winning_trades - losing_trades,
            'average_win': avg_win,
            'average_loss': avg_loss,
            'profit_factor': abs(avg_win / avg_loss) if avg_loss != 0 else float('inf'),
            'max_concurrent_positions': self.max_concurrent_positions,
            'position_utilization': len(self.open_positions) / self.max_concurrent_positions
        }
    
    def reset(self) -> None:
        """
        Reset the position manager (clear all positions and statistics).
        """
        self.positions.clear()
        self.open_positions.clear()
        self.closed_positions.clear()
        self.total_positions_opened = 0
        self.total_positions_closed = 0
        self.total_pnl = 0.0
        
        self.logger.info("Position manager reset")
    
    def __str__(self) -> str:
        """String representation of the position manager."""
        stats = self.get_position_statistics()
        return (f"PositionManager(open: {stats['current_open_positions']}, "
                f"closed: {stats['total_positions_closed']}, "
                f"PnL: {stats['total_pnl']:.2f})")
    
    def __repr__(self) -> str:
        """Detailed representation of the position manager."""
        return self.__str__()
