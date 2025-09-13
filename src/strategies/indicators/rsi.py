"""
Relative Strength Index (RSI) Indicator

This module provides RSI calculation functionality for trading strategies.
"""

import numpy as np
from typing import List, Union

def calculate_rsi(prices: List[Union[float, int]], period: int = 14) -> float:
    """
    Calculate the Relative Strength Index (RSI) for a given price series.
    
    Args:
        prices: List of price values
        period: RSI calculation period (default: 14)
        
    Returns:
        RSI value between 0 and 100
        
    Raises:
        ValueError: If period is invalid or insufficient data
    """
    if period <= 0:
        raise ValueError("Period must be positive")
    
    if len(prices) < period + 1:
        raise ValueError(f"Insufficient data: need at least {period + 1} prices, got {len(prices)}")
    
    # Convert to numpy array for efficient calculations
    prices_array = np.array(prices, dtype=float)
    
    # Calculate price changes
    price_changes = np.diff(prices_array)
    
    # Separate gains and losses
    gains = np.where(price_changes > 0, price_changes, 0)
    losses = np.where(price_changes < 0, -price_changes, 0)
    
    # Calculate average gains and losses using simple moving average
    avg_gains = np.mean(gains[:period])
    avg_losses = np.mean(losses[:period])
    
    # Calculate RSI
    if avg_losses == 0:
        return 100.0
    
    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))
    
    return float(rsi)

def calculate_rsi_smoothed(prices: List[Union[float, int]], period: int = 14) -> float:
    """
    Calculate RSI using smoothed averages (exponential moving average).
    
    Args:
        prices: List of price values
        period: RSI calculation period (default: 14)
        
    Returns:
        Smoothed RSI value between 0 and 100
    """
    if period <= 0:
        raise ValueError("Period must be positive")
    
    if len(prices) < period + 1:
        raise ValueError(f"Insufficient data: need at least {period + 1} prices, got {len(prices)}")
    
    # Convert to numpy array
    prices_array = np.array(prices, dtype=float)
    
    # Calculate price changes
    price_changes = np.diff(prices_array)
    
    # Separate gains and losses
    gains = np.where(price_changes > 0, price_changes, 0)
    losses = np.where(price_changes < 0, -price_changes, 0)
    
    # Calculate smoothed averages using exponential moving average
    alpha = 1.0 / period
    
    # Initialize with simple average
    avg_gains = np.mean(gains[:period])
    avg_losses = np.mean(losses[:period])
    
    # Apply exponential smoothing to remaining values
    for i in range(period, len(gains)):
        avg_gains = alpha * gains[i] + (1 - alpha) * avg_gains
        avg_losses = alpha * losses[i] + (1 - alpha) * avg_losses
    
    # Calculate RSI
    if avg_losses == 0:
        return 100.0
    
    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))
    
    return float(rsi)

def calculate_rsi_divergence(prices: List[Union[float, int]], 
                           rsi_values: List[float]) -> dict:
    """
    Calculate RSI divergence patterns.
    
    Args:
        prices: List of price values
        rsi_values: List of corresponding RSI values
        
    Returns:
        Dictionary containing divergence information
    """
    if len(prices) != len(rsi_values) or len(prices) < 10:
        return {'divergence': 'insufficient_data'}
    
    # Find local peaks and troughs
    price_peaks = []
    price_troughs = []
    rsi_peaks = []
    rsi_troughs = []
    
    for i in range(1, len(prices) - 1):
        # Price peaks
        if prices[i] > prices[i-1] and prices[i] > prices[i+1]:
            price_peaks.append((i, prices[i]))
        
        # Price troughs
        if prices[i] < prices[i-1] and prices[i] < prices[i+1]:
            price_troughs.append((i, prices[i]))
        
        # RSI peaks
        if rsi_values[i] > rsi_values[i-1] and rsi_values[i] > rsi_values[i+1]:
            rsi_peaks.append((i, rsi_values[i]))
        
        # RSI troughs
        if rsi_values[i] < rsi_values[i-1] and rsi_values[i] < rsi_values[i+1]:
            rsi_troughs.append((i, rsi_values[i]))
    
    # Check for bullish divergence (price lower lows, RSI higher lows)
    bullish_divergence = False
    if len(price_troughs) >= 2 and len(rsi_troughs) >= 2:
        if (price_troughs[-1][1] < price_troughs[-2][1] and 
            rsi_troughs[-1][1] > rsi_troughs[-2][1]):
            bullish_divergence = True
    
    # Check for bearish divergence (price higher highs, RSI lower highs)
    bearish_divergence = False
    if len(price_peaks) >= 2 and len(rsi_peaks) >= 2:
        if (price_peaks[-1][1] > price_peaks[-2][1] and 
            rsi_peaks[-1][1] < rsi_peaks[-2][1]):
            bearish_divergence = True
    
    return {
        'divergence': 'none',
        'bullish_divergence': bullish_divergence,
        'bearish_divergence': bearish_divergence,
        'price_peaks': len(price_peaks),
        'price_troughs': len(price_troughs),
        'rsi_peaks': len(rsi_peaks),
        'rsi_troughs': len(rsi_troughs)
    }

def is_rsi_overbought(rsi_value: float, threshold: float = 70) -> bool:
    """
    Check if RSI indicates overbought conditions.
    
    Args:
        rsi_value: Current RSI value
        threshold: Overbought threshold (default: 70)
        
    Returns:
        True if overbought, False otherwise
    """
    return rsi_value >= threshold

def is_rsi_oversold(rsi_value: float, threshold: float = 30) -> bool:
    """
    Check if RSI indicates oversold conditions.
    
    Args:
        rsi_value: Current RSI value
        threshold: Oversold threshold (default: 30)
        
    Returns:
        True if oversold, False otherwise
    """
    return rsi_value <= threshold
