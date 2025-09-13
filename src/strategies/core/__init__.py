"""
Core Trading Strategies

This module contains the core trading strategies that form the foundation
of the trading system. These are the original, well-tested strategies.
"""

from .bbrsi_strategy import BBRSIStrategy
from .scalping_strategy import ScalpingStrategy

__all__ = ['BBRSIStrategy', 'ScalpingStrategy']
