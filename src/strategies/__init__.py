"""
Trading Strategies Module

This module contains all trading strategies for the Hyperliquid trading bot.
Strategies are organized into:
- core: Original, well-tested strategies (BBRSI, Scalping)
- timeframe_optimized: Best-performing strategies for specific timeframes
- indicators: Technical analysis indicators

Only the best-performing strategies are kept for production use.
"""

from .strategy_factory import StrategyFactory

# Import core strategies
from .core.bbrsi_strategy import BBRSIStrategy
from .core.scalping_strategy import ScalpingStrategy

# Import timeframe-optimized strategies
from .timeframe_optimized.super_optimized_strategy import SuperOptimizedStrategy
from .timeframe_optimized.super_optimized_5m_strategy import SuperOptimized5mStrategy
from .timeframe_optimized.super_optimized_15m_strategy import SuperOptimized15mStrategy

__all__ = [
    'StrategyFactory',
    'BBRSIStrategy', 
    'ScalpingStrategy',
    'SuperOptimizedStrategy', 
    'SuperOptimized5mStrategy', 
    'SuperOptimized15mStrategy'
]
