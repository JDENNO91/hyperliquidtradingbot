"""
Average Directional Index (ADX) Indicator

This module provides ADX calculation functionality for trading strategies.
"""

import numpy as np
from typing import List, Union, Dict, Tuple

def calculate_adx(highs: List[Union[float, int]], 
                 lows: List[Union[float, int]], 
                 closes: List[Union[float, int]], 
                 period: int = 14) -> Dict[str, float]:
    """
    Calculate the Average Directional Index (ADX) and related indicators.
    
    Args:
        highs: List of high prices
        lows: List of low prices
        closes: List of close prices
        period: ADX calculation period (default: 14)
        
    Returns:
        Dictionary containing ADX, +DI, -DI values
        
    Raises:
        ValueError: If period is invalid or insufficient data
    """
    if period <= 0:
        raise ValueError("Period must be positive")
    
    if len(highs) != len(lows) or len(highs) != len(closes):
        raise ValueError("All price arrays must have the same length")
    
    if len(highs) < period + 1:
        raise ValueError(f"Insufficient data: need at least {period + 1} prices, got {len(highs)}")
    
    # Convert to numpy arrays for efficient calculations
    highs_array = np.array(highs, dtype=float)
    lows_array = np.array(lows, dtype=float)
    closes_array = np.array(closes, dtype=float)
    
    # Calculate True Range (TR)
    tr = calculate_true_range(highs_array, lows_array, closes_array)
    
    # Calculate Directional Movement (+DM and -DM)
    plus_dm, minus_dm = calculate_directional_movement(highs_array, lows_array)
    
    # Calculate smoothed TR, +DM, and -DM using Wilder's smoothing
    smoothed_tr = wilder_smoothing(tr, period)
    smoothed_plus_dm = wilder_smoothing(plus_dm, period)
    smoothed_minus_dm = wilder_smoothing(minus_dm, period)
    
    # Calculate +DI and -DI (suppress division warnings)
    with np.errstate(divide='ignore', invalid='ignore'):
        plus_di = np.where(smoothed_tr != 0, (smoothed_plus_dm / smoothed_tr) * 100, 0)
        minus_di = np.where(smoothed_tr != 0, (smoothed_minus_dm / smoothed_tr) * 100, 0)
        
        # Calculate DX (Directional Index)
        dx = np.where((plus_di + minus_di) != 0, 
                      np.abs(plus_di - minus_di) / (plus_di + minus_di) * 100, 0)
    
    # Calculate ADX (smoothed DX)
    adx = wilder_smoothing(dx, period)
    
    # Get the latest values
    latest_adx = float(adx[-1]) if len(adx) > 0 else 0.0
    latest_plus_di = float(plus_di[-1]) if len(plus_di) > 0 else 0.0
    latest_minus_di = float(minus_di[-1]) if len(minus_di) > 0 else 0.0
    
    return {
        'adx': latest_adx,
        'plus_di': latest_plus_di,
        'minus_di': latest_minus_di,
        'dx': float(dx[-1]) if len(dx) > 0 else 0.0,
        'tr': float(tr[-1]) if len(tr) > 0 else 0.0
    }

def calculate_true_range(highs: np.ndarray, 
                        lows: np.ndarray, 
                        closes: np.ndarray) -> np.ndarray:
    """
    Calculate True Range for ADX calculation.
    
    Args:
        highs: Array of high prices
        lows: Array of low prices
        closes: Array of close prices
        
    Returns:
        Array of True Range values
    """
    # Previous close prices (shifted by 1)
    prev_closes = np.roll(closes, 1)
    prev_closes[0] = closes[0]  # First element same as first close
    
    # Calculate the three components of True Range
    high_low = highs - lows
    high_prev_close = np.abs(highs - prev_closes)
    low_prev_close = np.abs(lows - prev_closes)
    
    # True Range is the maximum of the three
    tr = np.maximum(high_low, np.maximum(high_prev_close, low_prev_close))
    
    return tr

def calculate_directional_movement(highs: np.ndarray, 
                                 lows: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate Directional Movement (+DM and -DM) for ADX calculation.
    
    Args:
        highs: Array of high prices
        lows: Array of low prices
        
    Returns:
        Tuple of (+DM, -DM) arrays
    """
    # Previous high and low prices
    prev_highs = np.roll(highs, 1)
    prev_lows = np.roll(lows, 1)
    prev_highs[0] = highs[0]  # First element same as first high
    prev_lows[0] = lows[0]     # First element same as first low
    
    # Calculate high and low differences
    high_diff = highs - prev_highs
    low_diff = prev_lows - lows
    
    # +DM: Current high - Previous high (if positive and greater than low difference)
    plus_dm = np.where((high_diff > low_diff) & (high_diff > 0), high_diff, 0)
    
    # -DM: Previous low - Current low (if positive and greater than high difference)
    minus_dm = np.where((low_diff > high_diff) & (low_diff > 0), low_diff, 0)
    
    return plus_dm, minus_dm

def wilder_smoothing(data: np.ndarray, period: int) -> np.ndarray:
    """
    Apply Wilder's smoothing to data (exponential-like smoothing).
    
    Args:
        data: Input data array
        period: Smoothing period
        
    Returns:
        Smoothed data array
    """
    if len(data) == 0:
        return data
    
    # Initialize smoothed array
    smoothed = np.zeros_like(data)
    
    # First value is simple average of first 'period' values
    if len(data) >= period:
        smoothed[period - 1] = np.mean(data[:period])
    else:
        smoothed[0] = np.mean(data)
        return smoothed
    
    # Apply Wilder's smoothing formula: Smoothed[i] = Smoothed[i-1] - (Smoothed[i-1]/period) + Current[i]
    for i in range(period, len(data)):
        smoothed[i] = smoothed[i-1] - (smoothed[i-1] / period) + data[i]
    
    return smoothed

def calculate_adx_trend_strength(adx_value: float, threshold: float = 25.0) -> str:
    """
    Determine trend strength based on ADX value.
    
    Args:
        adx_value: Current ADX value
        threshold: ADX threshold for strong trend (default: 25.0)
        
    Returns:
        Trend strength description
    """
    if adx_value >= threshold:
        return "strong"
    elif adx_value >= 20.0:
        return "moderate"
    else:
        return "weak"

def is_trend_strong(adx_value: float, threshold: float = 25.0) -> bool:
    """
    Check if trend is strong based on ADX value.
    
    Args:
        adx_value: Current ADX value
        threshold: ADX threshold for strong trend (default: 25.0)
        
    Returns:
        True if trend is strong, False otherwise
    """
    return adx_value >= threshold

def calculate_di_spread(plus_di: float, minus_di: float) -> float:
    """
    Calculate the spread between +DI and -DI.
    
    Args:
        plus_di: Positive Directional Indicator value
        minus_di: Negative Directional Indicator value
        
    Returns:
        DI spread value
    """
    return abs(plus_di - minus_di)

def is_bullish_trend(plus_di: float, minus_di: float) -> bool:
    """
    Check if trend is bullish based on DI values.
    
    Args:
        plus_di: Positive Directional Indicator value
        minus_di: Negative Directional Indicator value
        
    Returns:
        True if trend is bullish, False otherwise
    """
    return plus_di > minus_di

def is_bearish_trend(plus_di: float, minus_di: float) -> bool:
    """
    Check if trend is bearish based on DI values.
    
    Args:
        plus_di: Positive Directional Indicator value
        minus_di: Negative Directional Indicator value
        
    Returns:
        True if trend is bearish, False otherwise
    """
    return minus_di > plus_di

def calculate_adx_momentum(adx_values: List[float], period: int = 5) -> float:
    """
    Calculate ADX momentum (rate of change).
    
    Args:
        adx_values: List of ADX values
        period: Period for momentum calculation (default: 5)
        
    Returns:
        Momentum value (positive = increasing, negative = decreasing)
    """
    if len(adx_values) < period + 1:
        return 0.0
    
    current_adx = adx_values[-1]
    previous_adx = adx_values[-period - 1]
    
    momentum = current_adx - previous_adx
    return float(momentum)

def detect_adx_divergence(price_values: List[float], 
                         adx_values: List[float], 
                         lookback: int = 10) -> Dict[str, bool]:
    """
    Detect ADX divergence patterns.
    
    Args:
        price_values: List of price values
        adx_values: List of ADX values
        lookback: Number of periods to look back (default: 10)
        
    Returns:
        Dictionary with divergence information
    """
    if len(price_values) < lookback or len(adx_values) < lookback:
        return {'divergence': 'insufficient_data'}
    
    # Get recent price and ADX movements
    recent_prices = price_values[-lookback:]
    recent_adx = adx_values[-lookback:]
    
    # Calculate price and ADX trends
    price_trend = recent_prices[-1] - recent_prices[0]
    adx_trend = recent_adx[-1] - recent_adx[0]
    
    # Detect divergence
    bullish_divergence = price_trend < 0 and adx_trend > 0  # Price down, ADX up
    bearish_divergence = price_trend > 0 and adx_trend < 0  # Price up, ADX down
    
    return {
        'divergence': 'none',
        'bullish_divergence': bullish_divergence,
        'bearish_divergence': bearish_divergence,
        'price_trend': price_trend,
        'adx_trend': adx_trend
    }
