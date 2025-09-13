# Exponential Moving Average (EMA) indicator functions

from typing import List, Dict, Optional

# Configuration for EMA periods (can be overridden by passing periods to functions)
DEFAULT_LONG_EMA_PERIOD = 14
DEFAULT_SHORT_EMA_PERIOD = 6

def short_ema(data: List[Dict], period: Optional[int] = None) -> List[Optional[float]]:
    """
    Compute the short-term EMA from candlestick data.
    Args:
        data (List[dict]): List of candlestick dicts with key "c" for close.
        period (int, optional): EMA period. Defaults to 12.
    Returns:
        List[Optional[float]]: EMA values aligned with input data (None for insufficient data).
    """
    price_data = get_price_data(data)
    return calculate_ema(price_data, period or DEFAULT_SHORT_EMA_PERIOD)

def long_ema(data: List[Dict], period: Optional[int] = None) -> List[Optional[float]]:
    """
    Compute the long-term EMA from candlestick data.
    Args:
        data (List[dict]): List of candlestick dicts with key "c" for close.
        period (int, optional): EMA period. Defaults to 26.
    Returns:
        List[Optional[float]]: EMA values aligned with input data (None for insufficient data).
    """
    price_data = get_price_data(data)
    return calculate_ema(price_data, period or DEFAULT_LONG_EMA_PERIOD)

def get_price_data(candles: List[Dict]) -> List[float]:
    """Extract and convert closing prices from candlestick data."""
    price_data = [float(candle["c"]) for candle in candles]
    return price_data

def calculate_ema(price_data: List[float], period: int) -> List[Optional[float]]:
    """
    Calculate the Exponential Moving Average (EMA) for given price data and period.
    Returns a list aligned with price_data (None for indices where EMA can't be computed).
    """
    if len(price_data) < period:
        # Not enough data for even one EMA value
        return [None] * len(price_data)
    # Calculate initial Simple Moving Average (SMA)
    initial_sma = sum(price_data[:period]) / period
    smoothing_factor = 2 / (period + 1)
    ema_values = [None] * (period - 1)  # Fill with None for indices before first EMA
    ema_values.append(initial_sma)

    # Compute subsequent EMA values using smoothing formula
    for i in range(period, len(price_data)):
        previous_ema = ema_values[-1]
        current_price = price_data[i]
        current_ema = (current_price - previous_ema) * smoothing_factor + previous_ema
        ema_values.append(current_ema)

    return ema_values

__all__ = ['short_ema', 'long_ema']
