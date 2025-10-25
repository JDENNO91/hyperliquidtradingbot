"""
Microprice calculation functions for trading strategies.

Microprice is a weighted average of bid and ask prices that provides
a more accurate representation of the current market price.
"""

from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np


class MicropriceData:
    """Data class for microprice information."""
    
    def __init__(self, microprice: float, bid: float, ask: float, spread: float, volume_weighted: bool = False):
        self.microprice = microprice
        self.bid = bid
        self.ask = ask
        self.spread = spread
        self.volume_weighted = volume_weighted


def calculate_microprice(bid: float, ask: float, bid_volume: float = 1.0, ask_volume: float = 1.0) -> float:
    """
    Calculate microprice from bid/ask prices and volumes.
    
    Args:
        bid: Bid price
        ask: Ask price
        bid_volume: Bid volume (default: 1.0)
        ask_volume: Ask volume (default: 1.0)
    
    Returns:
        Microprice value
    """
    if bid <= 0 or ask <= 0:
        return (bid + ask) / 2
    
    if bid_volume <= 0:
        bid_volume = 1.0
    if ask_volume <= 0:
        ask_volume = 1.0
    
    total_volume = bid_volume + ask_volume
    return (bid * ask_volume + ask * bid_volume) / total_volume


def calculate_microprice_from_orderbook(orderbook: Dict[str, Any]) -> MicropriceData:
    """
    Calculate microprice from orderbook data.
    
    Args:
        orderbook: Orderbook data with bids and asks
    
    Returns:
        MicropriceData object
    """
    try:
        bids = orderbook.get('bids', [])
        asks = orderbook.get('asks', [])
        
        if not bids or not asks:
            # Fallback to mid price
            mid_price = (orderbook.get('bid', 0) + orderbook.get('ask', 0)) / 2
            return MicropriceData(mid_price, orderbook.get('bid', 0), orderbook.get('ask', 0), 0)
        
        best_bid = float(bids[0][0]) if bids else 0
        best_ask = float(asks[0][0]) if asks else 0
        bid_volume = float(bids[0][1]) if bids else 1.0
        ask_volume = float(asks[0][1]) if asks else 1.0
        
        microprice = calculate_microprice(best_bid, best_ask, bid_volume, ask_volume)
        spread = best_ask - best_bid
        
        return MicropriceData(microprice, best_bid, best_ask, spread, volume_weighted=True)
        
    except (IndexError, ValueError, TypeError):
        # Fallback calculation
        bid = orderbook.get('bid', 0)
        ask = orderbook.get('ask', 0)
        mid_price = (bid + ask) / 2
        return MicropriceData(mid_price, bid, ask, ask - bid)


def calculate_microprice_from_ohlcv(data: List[Dict[str, Any]], index: int = -1) -> MicropriceData:
    """
    Calculate microprice from OHLCV data.
    
    Args:
        data: List of OHLCV candles
        index: Index of the candle to use (default: -1 for latest)
    
    Returns:
        MicropriceData object
    """
    if not data or len(data) == 0:
        return MicropriceData(0, 0, 0, 0)
    
    try:
        candle = data[index]
        high = float(candle.get('h', 0))
        low = float(candle.get('l', 0))
        close = float(candle.get('c', 0))
        volume = float(candle.get('v', 1))
        
        # Use high/low as bid/ask approximation
        # In real trading, you'd have actual bid/ask data
        bid = low
        ask = high
        
        # Calculate microprice using volume as weight
        microprice = calculate_microprice(bid, ask, volume, volume)
        spread = ask - bid
        
        return MicropriceData(microprice, bid, ask, spread, volume_weighted=True)
        
    except (IndexError, ValueError, TypeError, KeyError):
        # Fallback to simple mid price
        try:
            candle = data[index]
            high = float(candle.get('h', 0))
            low = float(candle.get('l', 0))
            mid_price = (high + low) / 2
            return MicropriceData(mid_price, low, high, high - low)
        except:
            return MicropriceData(0, 0, 0, 0)


def calculate_microprice_series(data: List[Dict[str, Any]], lookback: int = 20) -> List[float]:
    """
    Calculate microprice series for a given dataset.
    
    Args:
        data: List of OHLCV candles
        lookback: Number of periods to look back
    
    Returns:
        List of microprice values
    """
    if not data or len(data) == 0:
        return []
    
    microprices = []
    start_index = max(0, len(data) - lookback)
    
    for i in range(start_index, len(data)):
        microprice_data = calculate_microprice_from_ohlcv(data, i)
        microprices.append(microprice_data.microprice)
    
    return microprices


def get_microprice_signals(microprices: List[float], threshold: float = 0.001) -> List[str]:
    """
    Generate trading signals based on microprice changes.
    
    Args:
        microprices: List of microprice values
        threshold: Minimum change threshold for signal generation
    
    Returns:
        List of signals ('BUY', 'SELL', 'HOLD')
    """
    if len(microprices) < 2:
        return ['HOLD']
    
    signals = []
    for i in range(1, len(microprices)):
        change = microprices[i] - microprices[i-1]
        change_pct = change / microprices[i-1] if microprices[i-1] != 0 else 0
        
        if change_pct > threshold:
            signals.append('BUY')
        elif change_pct < -threshold:
            signals.append('SELL')
        else:
            signals.append('HOLD')
    
    return signals


def calculate_microprice_momentum(microprices: List[float], period: int = 5) -> float:
    """
    Calculate microprice momentum over a given period.
    
    Args:
        microprices: List of microprice values
        period: Number of periods for momentum calculation
    
    Returns:
        Momentum value (positive = upward, negative = downward)
    """
    if len(microprices) < period:
        return 0.0
    
    recent = microprices[-period:]
    older = microprices[-period-1:-1] if len(microprices) > period else recent
    
    if len(older) == 0:
        return 0.0
    
    momentum = (sum(recent) / len(recent)) - (sum(older) / len(older))
    return momentum


def calculate_microprice_volatility(microprices: List[float], period: int = 20) -> float:
    """
    Calculate microprice volatility over a given period.
    
    Args:
        microprices: List of microprice values
        period: Number of periods for volatility calculation
    
    Returns:
        Volatility value (standard deviation)
    """
    if len(microprices) < period:
        return 0.0
    
    recent_prices = microprices[-period:]
    return float(np.std(recent_prices))


def calculate_microprice_trend(microprices: List[float], period: int = 10) -> str:
    """
    Determine microprice trend over a given period.
    
    Args:
        microprices: List of microprice values
        period: Number of periods for trend calculation
    
    Returns:
        Trend direction ('UP', 'DOWN', 'SIDEWAYS')
    """
    if len(microprices) < period:
        return 'SIDEWAYS'
    
    recent_prices = microprices[-period:]
    first_half = recent_prices[:period//2]
    second_half = recent_prices[period//2:]
    
    first_avg = sum(first_half) / len(first_half)
    second_avg = sum(second_half) / len(second_half)
    
    change_pct = (second_avg - first_avg) / first_avg if first_avg != 0 else 0
    
    if change_pct > 0.01:  # 1% threshold
        return 'UP'
    elif change_pct < -0.01:
        return 'DOWN'
    else:
        return 'SIDEWAYS'
