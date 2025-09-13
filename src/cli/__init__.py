"""
CLI Package

This package provides command-line interfaces for all major functionalities.
"""

from .backtest import backtest_cli
from .optimize import optimize_cli
from .simulate import simulate_cli
from .trade import trade_cli

__all__ = [
    'backtest_cli',
    'optimize_cli',
    'simulate_cli',
    'trade_cli'
]
