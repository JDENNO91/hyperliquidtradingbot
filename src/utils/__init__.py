"""
Utilities Package

This package provides common utility functions for the trading system.
"""

from .logger import (
    setup_logger,
    get_logger,
    setup_file_logging,
    setup_rotating_file_logging,
    setup_timed_file_logging,
    setup_logging_from_config
)

from .data_loader import (
    load_market_data,
    load_json_data,
    load_csv_data,
    load_parquet_data,
    save_market_data,
    save_json_data,
    save_csv_data,
    save_parquet_data,
    validate_market_data,
    filter_market_data,
    resample_market_data,
    merge_market_data
)

from .performance import (
    calculate_metrics,
    calculate_equity_curve,
    calculate_max_drawdown,
    calculate_returns,
    calculate_sharpe_ratio,
    calculate_calmar_ratio,
    calculate_sortino_ratio,
    calculate_win_loss_ratio,
    calculate_consecutive_wins_losses,
    calculate_risk_reward_ratio,
    calculate_position_sizing_metrics,
    generate_performance_report
)

__all__ = [
    # Logging utilities
    'setup_logger',
    'get_logger',
    'setup_file_logging',
    'setup_rotating_file_logging',
    'setup_timed_file_logging',
    'setup_logging_from_config',
    
    # Data loading utilities
    'load_market_data',
    'load_json_data',
    'load_csv_data',
    'load_parquet_data',
    'save_market_data',
    'save_json_data',
    'save_csv_data',
    'save_parquet_data',
    'validate_market_data',
    'filter_market_data',
    'resample_market_data',
    'merge_market_data',
    
    # Performance utilities
    'calculate_metrics',
    'calculate_equity_curve',
    'calculate_max_drawdown',
    'calculate_returns',
    'calculate_sharpe_ratio',
    'calculate_calmar_ratio',
    'calculate_sortino_ratio',
    'calculate_win_loss_ratio',
    'calculate_consecutive_wins_losses',
    'calculate_risk_reward_ratio',
    'calculate_position_sizing_metrics',
    'generate_performance_report'
]
