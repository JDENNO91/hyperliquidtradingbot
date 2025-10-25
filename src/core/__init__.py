"""
Core Package

This package provides the core trading engine components.
Only the improved versions are kept for production use.
"""

from .base_strategy import BaseStrategy, Signal, Position
from .improved_trading_engine import ImprovedTradingEngine
from .improved_position_manager import ImprovedPositionManager
from .simple_risk_manager import SimpleRiskManager

__all__ = [
    'BaseStrategy',
    'Signal',
    'Position',
    'ImprovedTradingEngine',
    'ImprovedPositionManager',
    'SimpleRiskManager'
]
