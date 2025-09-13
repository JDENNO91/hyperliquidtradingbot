"""
Technical Indicators Package

This package provides modular technical indicator calculations for trading strategies.
"""

from .rsi import (
    calculate_rsi,
    calculate_rsi_smoothed,
    calculate_rsi_divergence,
    is_rsi_overbought,
    is_rsi_oversold
)

from .bollinger_bands import (
    calculate_bollinger_bands,
    calculate_bollinger_bands_rolling,
    calculate_bollinger_bandwidth,
    is_price_in_bands,
    detect_bollinger_squeeze,
    calculate_bollinger_support_resistance,
    calculate_bollinger_momentum
)

from .adx import (
    calculate_adx,
    calculate_adx_trend_strength,
    is_trend_strong,
    calculate_di_spread,
    is_bullish_trend,
    is_bearish_trend,
    calculate_adx_momentum,
    detect_adx_divergence
)

__all__ = [
    # RSI indicators
    'calculate_rsi',
    'calculate_rsi_smoothed',
    'calculate_rsi_divergence',
    'is_rsi_overbought',
    'is_rsi_oversold',
    
    # Bollinger Bands indicators
    'calculate_bollinger_bands',
    'calculate_bollinger_bands_rolling',
    'calculate_bollinger_bandwidth',
    'is_price_in_bands',
    'detect_bollinger_squeeze',
    'calculate_bollinger_support_resistance',
    'calculate_bollinger_momentum',
    
    # ADX indicators
    'calculate_adx',
    'calculate_adx_trend_strength',
    'is_trend_strong',
    'calculate_di_spread',
    'is_bullish_trend',
    'is_bearish_trend',
    'calculate_adx_momentum',
    'detect_adx_divergence'
]