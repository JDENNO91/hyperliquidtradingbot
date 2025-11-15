"""
Execution Simulator for Backtesting

Simulates realistic order execution with:
- Slippage modeling
- Transaction fees
- Order execution latency
- Partial fills
- Liquidity constraints
"""

import random
import time
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of order execution simulation."""
    executed_price: float
    executed_size: float
    slippage: float
    fee: float
    execution_time_ms: float
    partial_fill: bool
    fill_percentage: float


class ExecutionSimulator:
    """
    Simulates realistic order execution for backtesting.
    
    This simulator models real-world trading conditions to provide
    more realistic backtest results.
    """
    
    def __init__(
        self,
        slippage: float = 0.001,  # 0.1% default slippage
        fee_rate: float = 0.0005,  # 0.05% default fee
        execution_latency_ms: float = 100.0,
        partial_fills: bool = False,
        liquidity_constraint: float = 1.0,
        random_seed: Optional[int] = None
    ):
        """
        Initialize execution simulator.
        
        Args:
            slippage: Slippage as fraction (0.001 = 0.1%)
            fee_rate: Trading fee rate (0.0005 = 0.05%)
            execution_latency_ms: Average execution latency in milliseconds
            partial_fills: Whether to simulate partial fills
            liquidity_constraint: Liquidity constraint factor (1.0 = no constraint)
            random_seed: Random seed for reproducibility
        """
        self.slippage = slippage
        self.fee_rate = fee_rate
        self.execution_latency_ms = execution_latency_ms
        self.partial_fills = partial_fills
        self.liquidity_constraint = liquidity_constraint
        
        if random_seed is not None:
            random.seed(random_seed)
        
        logger.info(
            f"ExecutionSimulator initialized: slippage={slippage:.4f}, "
            f"fee_rate={fee_rate:.4f}, latency={execution_latency_ms}ms"
        )
    
    def execute_order(
        self,
        order_type: str,  # 'MARKET', 'LIMIT'
        side: str,  # 'LONG' (buy) or 'SHORT' (sell)
        size: float,
        price: float,
        current_bid: Optional[float] = None,
        current_ask: Optional[float] = None,
        volume: Optional[float] = None
    ) -> ExecutionResult:
        """
        Simulate order execution.
        
        Args:
            order_type: Order type ('MARKET' or 'LIMIT')
            side: Trade side ('LONG' for buy, 'SHORT' for sell)
            size: Order size
            price: Limit price (for limit orders) or current price (for market orders)
            current_bid: Current bid price (optional, for better slippage calculation)
            current_ask: Current ask price (optional, for better slippage calculation)
            volume: Current volume (optional, for liquidity modeling)
            
        Returns:
            ExecutionResult with execution details
        """
        # Simulate execution latency
        execution_time_ms = self._simulate_latency()
        
        # Calculate executed price with slippage
        executed_price = self._calculate_executed_price(
            order_type, side, price, current_bid, current_ask
        )
        
        # Simulate partial fills if enabled
        executed_size, partial_fill, fill_percentage = self._simulate_fill(
            size, volume
        )
        
        # Calculate slippage
        slippage = abs(executed_price - price) / price if price > 0 else 0.0
        
        # Calculate fee
        fee = executed_size * executed_price * self.fee_rate
        
        return ExecutionResult(
            executed_price=executed_price,
            executed_size=executed_size,
            slippage=slippage,
            fee=fee,
            execution_time_ms=execution_time_ms,
            partial_fill=partial_fill,
            fill_percentage=fill_percentage
        )
    
    def _calculate_executed_price(
        self,
        order_type: str,
        side: str,
        price: float,
        current_bid: Optional[float],
        current_ask: Optional[float]
    ) -> float:
        """Calculate executed price with slippage."""
        if order_type == 'LIMIT':
            # Limit orders execute at limit price (no slippage)
            return price
        
        # Market orders have slippage
        if side == 'LONG':  # Buying
            # Buy at ask price + slippage
            if current_ask:
                base_price = current_ask
            else:
                base_price = price
            
            # Slippage increases price (worse for buyer)
            slippage_factor = 1.0 + self.slippage
            # Add some randomness (±50% of slippage)
            random_factor = 1.0 + random.uniform(-0.5, 0.5) * self.slippage
            return base_price * slippage_factor * random_factor
        
        else:  # SHORT (selling)
            # Sell at bid price - slippage
            if current_bid:
                base_price = current_bid
            else:
                base_price = price
            
            # Slippage decreases price (worse for seller)
            slippage_factor = 1.0 - self.slippage
            # Add some randomness (±50% of slippage)
            random_factor = 1.0 + random.uniform(-0.5, 0.5) * self.slippage
            return base_price * slippage_factor * random_factor
    
    def _simulate_latency(self) -> float:
        """Simulate execution latency."""
        # Exponential distribution for latency (more realistic)
        # Mean = execution_latency_ms
        latency = random.expovariate(1.0 / self.execution_latency_ms)
        return min(latency, self.execution_latency_ms * 5)  # Cap at 5x mean
    
    def _simulate_fill(
        self,
        order_size: float,
        available_volume: Optional[float]
    ) -> Tuple[float, bool, float]:
        """
        Simulate order fill (potentially partial).
        
        Returns:
            Tuple of (executed_size, is_partial_fill, fill_percentage)
        """
        if not self.partial_fills:
            return order_size, False, 1.0
        
        # If liquidity constraint is enabled and volume is available
        if available_volume is not None and self.liquidity_constraint < 1.0:
            # Calculate maximum fillable size based on liquidity
            max_fillable = available_volume * self.liquidity_constraint
            
            if order_size > max_fillable:
                # Partial fill
                fill_percentage = max_fillable / order_size
                executed_size = max_fillable
                return executed_size, True, fill_percentage
        
        # Full fill (with small chance of partial fill even with sufficient liquidity)
        if random.random() < 0.05:  # 5% chance of partial fill
            fill_percentage = random.uniform(0.8, 0.99)
            executed_size = order_size * fill_percentage
            return executed_size, True, fill_percentage
        
        return order_size, False, 1.0
    
    def calculate_total_cost(
        self,
        executed_price: float,
        executed_size: float,
        fee: float
    ) -> float:
        """
        Calculate total cost including fees.
        
        Args:
            executed_price: Price per unit
            executed_size: Size executed
            fee: Trading fee
            
        Returns:
            Total cost
        """
        return (executed_price * executed_size) + fee
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution simulator statistics."""
        return {
            'slippage': self.slippage,
            'fee_rate': self.fee_rate,
            'execution_latency_ms': self.execution_latency_ms,
            'partial_fills_enabled': self.partial_fills,
            'liquidity_constraint': self.liquidity_constraint
        }


