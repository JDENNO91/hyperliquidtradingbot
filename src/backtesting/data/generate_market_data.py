"""
Market Data Generator

This script generates realistic market data for backtesting different cryptocurrencies.
"""

import json
import random
import math
from datetime import datetime, timedelta
from pathlib import Path


def generate_candles(symbol, timeframe, days=30, base_price=100):
    """
    Generate realistic OHLCV data for a given symbol and timeframe.
    
    Args:
        symbol: Trading symbol (e.g., 'SOL-PERP')
        timeframe: Timeframe in minutes (e.g., 1, 5, 15, 60)
        days: Number of days to generate
        base_price: Starting price for the asset
    
    Returns:
        List of OHLCV candles
    """
    candles = []
    current_time = datetime.now() - timedelta(days=days)
    current_price = base_price
    
    # Calculate number of candles needed
    minutes_per_day = 24 * 60
    total_candles = (days * minutes_per_day) // timeframe
    
    # Volatility settings for different assets
    volatility_settings = {
        'SOL-PERP': {'volatility': 0.03, 'trend': 0.001},
        'AVAX-PERP': {'volatility': 0.025, 'trend': 0.0008},
        'MATIC-PERP': {'volatility': 0.02, 'trend': 0.0005},
        'ETH-PERP': {'volatility': 0.02, 'trend': 0.0003},
        'BTC-PERP': {'volatility': 0.015, 'trend': 0.0002},
    }
    
    settings = volatility_settings.get(symbol, {'volatility': 0.02, 'trend': 0.001})
    volatility = settings['volatility']
    trend = settings['trend']
    
    for i in range(total_candles):
        # Add some trend and random walk
        price_change = random.gauss(trend, volatility)
        current_price *= (1 + price_change)
        
        # Generate OHLC from current price
        high_factor = random.uniform(1.001, 1.01)
        low_factor = random.uniform(0.99, 0.999)
        
        open_price = current_price
        high_price = current_price * high_factor
        low_price = current_price * low_factor
        close_price = current_price * random.uniform(0.995, 1.005)
        
        # Generate volume (higher during volatile periods)
        base_volume = 1000
        volume_multiplier = 1 + abs(price_change) * 10
        volume = int(base_volume * volume_multiplier * random.uniform(0.5, 2.0))
        
        candle = {
            "t": int(current_time.timestamp() * 1000),
            "o": round(open_price, 2),
            "h": round(high_price, 2),
            "l": round(low_price, 2),
            "c": round(close_price, 2),
            "v": volume
        }
        
        candles.append(candle)
        current_time += timedelta(minutes=timeframe)
        current_price = close_price
    
    return candles


def generate_all_market_data():
    """Generate market data for all supported symbols and timeframes."""
    
    symbols = ['SOL-PERP', 'AVAX-PERP', 'MATIC-PERP']
    timeframes = [1, 5, 15, 60]  # 1m, 5m, 15m, 1h
    base_prices = {
        'SOL-PERP': 50,
        'AVAX-PERP': 25,
        'MATIC-PERP': 0.8
    }
    
    for symbol in symbols:
        symbol_dir = Path(f"src/backtesting/data/{symbol}")
        symbol_dir.mkdir(exist_ok=True)
        
        for timeframe in timeframes:
            print(f"Generating {symbol} {timeframe}m data...")
            
            candles = generate_candles(
                symbol=symbol,
                timeframe=timeframe,
                days=30,
                base_price=base_prices[symbol]
            )
            
            # Save to file
            filename = f"{symbol}-{timeframe}m.json"
            filepath = symbol_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(candles, f, indent=2)
            
            print(f"  Generated {len(candles)} candles for {filename}")
    
    print("Market data generation complete!")


if __name__ == "__main__":
    generate_all_market_data()
