"""
Bollinger Bands Indicator

This module provides Bollinger Bands calculation functionality for trading strategies.
"""

import numpy as np
from typing import List, Union, Dict, Tuple

def calculate_bollinger_bands(prices: List[Union[float, int]], 
                             period: int = 20, 
                             std_dev: float = 2.0) -> Dict[str, float]:
    """
    Calculate Bollinger Bands for a given price series.
    
    Args:
        prices: List of price values
        period: Moving average period (default: 20)
        std_dev: Standard deviation multiplier (default: 2.0)
        
    Returns:
        Dictionary containing upper, middle, and lower bands
        
    Raises:
        ValueError: If period is invalid or insufficient data
    """
    if period <= 0:
        raise ValueError("Period must be positive")
    
    if std_dev <= 0:
        raise ValueError("Standard deviation must be positive")
    
    if len(prices) < period:
        raise ValueError(f"Insufficient data: need at least {period} prices, got {len(prices)}")
    
    # Convert to numpy array for efficient calculations
    prices_array = np.array(prices, dtype=float)
    
    # Calculate simple moving average (middle band)
    middle_band = np.mean(prices_array[-period:])
    
    # Calculate standard deviation
    std = np.std(prices_array[-period:])
    
    # Calculate upper and lower bands
    upper_band = middle_band + (std_dev * std)
    lower_band = middle_band - (std_dev * std)
    
    return {
        'upper': float(upper_band),
        'middle': float(middle_band),
        'lower': float(lower_band),
        'std': float(std),
        'width': float(upper_band - lower_band),
        'percent_b': float((prices_array[-1] - lower_band) / (upper_band - lower_band)) if upper_band != lower_band else 0.5
    }

def calculate_bollinger_bands_rolling(prices: List[Union[float, int]], 
                                    period: int = 20, 
                                    std_dev: float = 2.0) -> List[Dict[str, float]]:
    """
    Calculate rolling Bollinger Bands for the entire price series.
    
    Args:
        prices: List of price values
        period: Moving average period (default: 20)
        std_dev: Standard deviation multiplier (default: 2.0)
        
    Returns:
        List of dictionaries containing bands for each period
    """
    if period <= 0:
        raise ValueError("Period must be positive")
    
    if std_dev <= 0:
        raise ValueError("Standard deviation must be positive")
    
    if len(prices) < period:
        raise ValueError(f"Insufficient data: need at least {period} prices, got {len(prices)}")
    
    # Convert to numpy array
    prices_array = np.array(prices, dtype=float)
    
    bands = []
    
    for i in range(period - 1, len(prices_array)):
        # Get the window of prices for this period
        window = prices_array[i - period + 1:i + 1]
        
        # Calculate bands for this window
        middle_band = np.mean(window)
        std = np.std(window)
        
        upper_band = middle_band + (std_dev * std)
        lower_band = middle_band - (std_dev * std)
        
        # Calculate percent B (position within bands)
        current_price = prices_array[i]
        if upper_band != lower_band:
            percent_b = (current_price - lower_band) / (upper_band - lower_band)
        else:
            percent_b = 0.5
        
        bands.append({
            'upper': float(upper_band),
            'middle': float(middle_band),
            'lower': float(lower_band),
            'std': float(std),
            'width': float(upper_band - lower_band),
            'percent_b': float(percent_b)
        })
    
    return bands

def calculate_bollinger_bandwidth(prices: List[Union[float, int]], 
                                period: int = 20, 
                                std_dev: float = 2.0) -> float:
    """
    Calculate Bollinger Bandwidth (normalized width).
    
    Args:
        prices: List of price values
        period: Moving average period (default: 20)
        std_dev: Standard deviation multiplier (default: 2.0)
        
    Returns:
        Bandwidth value (0-1 scale)
    """
    bands = calculate_bollinger_bands(prices, period, std_dev)
    middle_band = bands['middle']
    
    if middle_band == 0:
        return 0.0
    
    # Normalize width by middle band
    bandwidth = bands['width'] / middle_band
    
    return float(bandwidth)

def is_price_in_bands(price: float, bands: Dict[str, float]) -> Dict[str, bool]:
    """
    Check if a price is within the Bollinger Bands.
    
    Args:
        price: Current price
        bands: Bollinger Bands dictionary
        
    Returns:
        Dictionary with position information
    """
    return {
        'above_upper': price > bands['upper'],
        'below_lower': price < bands['lower'],
        'between_bands': bands['lower'] <= price <= bands['upper'],
        'near_upper': price >= bands['upper'] * 0.98,  # Within 2% of upper
        'near_lower': price <= bands['lower'] * 1.02,  # Within 2% of lower
        'near_middle': abs(price - bands['middle']) <= (bands['width'] * 0.1)  # Within 10% of middle
    }

def detect_bollinger_squeeze(prices: List[Union[float, int]], 
                            period: int = 20, 
                            std_dev: float = 2.0,
                            threshold: float = 0.1) -> bool:
    """
    Detect Bollinger Band squeeze (low volatility period).
    
    Args:
        prices: List of price values
        period: Moving average period (default: 20)
        std_dev: Standard deviation multiplier (default: 2.0)
        threshold: Squeeze threshold (default: 0.1)
        
    Returns:
        True if squeeze detected, False otherwise
    """
    bandwidth = calculate_bollinger_bandwidth(prices, period, std_dev)
    return bandwidth <= threshold

def calculate_bollinger_support_resistance(prices: List[Union[float, int]], 
                                        period: int = 20, 
                                        std_dev: float = 2.0) -> Dict[str, float]:
    """
    Calculate potential support and resistance levels using Bollinger Bands.
    
    Args:
        prices: List of price values
        period: Moving average period (default: 20)
        std_dev: Standard deviation multiplier (default: 2.0)
        
    Returns:
        Dictionary with support and resistance levels
    """
    bands = calculate_bollinger_bands(prices, period, std_dev)
    
    # Use lower band as support, upper band as resistance
    support = bands['lower']
    resistance = bands['upper']
    
    # Calculate additional levels
    middle = bands['middle']
    std = bands['std']
    
    # Fibonacci-like levels within the bands
    fib_236 = middle - (0.236 * std * std_dev)
    fib_382 = middle - (0.382 * std * std_dev)
    fib_618 = middle + (0.618 * std * std_dev)
    fib_764 = middle + (0.764 * std * std_dev)
    
    return {
        'support': float(support),
        'resistance': float(resistance),
        'middle': float(middle),
        'fib_236': float(fib_236),
        'fib_382': float(fib_382),
        'fib_618': float(fib_618),
        'fib_764': float(fib_764)
    }

def calculate_bollinger_momentum(prices: List[Union[float, int]], 
                               period: int = 20, 
                               std_dev: float = 2.0) -> float:
    """
    Calculate momentum using Bollinger Bands position.
    
    Args:
        prices: List of price values
        period: Moving average period (default: 20)
        std_dev: Standard deviation multiplier (default: 2.0)
        
    Returns:
        Momentum value (-1 to 1, where 0 is neutral)
    """
    bands = calculate_bollinger_bands(prices, period, std_dev)
    current_price = prices[-1]
    
    # Calculate position within bands (-1 to 1)
    if bands['upper'] == bands['lower']:
        return 0.0
    
    # Normalize position: -1 (at lower band) to 1 (at upper band)
    position = (current_price - bands['lower']) / (bands['upper'] - bands['lower'])
    momentum = (position - 0.5) * 2  # Convert to -1 to 1 scale
    
    return float(momentum)
