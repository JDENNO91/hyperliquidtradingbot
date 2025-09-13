#!/usr/bin/env python3
"""
ETH Market Data Generator

This script generates synthetic ETH market data for backtesting purposes.
It creates realistic-looking candlestick data with proper OHLCV structure.

Usage:
    python3 generate_eth_candles.py

Output:
    ETH-PERP-1m.json - Generated market data file
"""

import json
from random import uniform, randint

# Configuration parameters
start_price = 2750.0  # Starting ETH price (realistic)
num_candles = 10000   # Number of candles to generate
interval_ms = 15 * 60 * 1000  # 15 minutes in milliseconds
start_timestamp = 1733299200000  # Starting timestamp (December 2024)

# Initialize data structures
candles = []
price = start_price

print(f"Generating {num_candles} ETH candles...")
print(f"Starting price: ${start_price}")
print(f"Interval: {interval_ms // 1000 // 60} minutes")

# Generate candlestick data
for i in range(num_candles):
    # Calculate timestamps
    t = start_timestamp + i * interval_ms  # Open time
    T = t + interval_ms - 1000  # Close time (1 second before next candle)
    
    # Simulate realistic price movement
    # Small random movement from previous close
    open_price = round(price + uniform(-5, 5), 2)
    # Larger movement for close price (more volatility)
    close_price = round(open_price + uniform(-7, 7), 2)
    
    # High and low prices based on open/close
    high_price = round(max(open_price, close_price) + uniform(0, 4), 2)
    low_price = round(min(open_price, close_price) - uniform(0, 4), 2)
    
    # Volume and trade count (realistic ranges)
    volume = round(uniform(100, 200), 2)
    trades = randint(180, 260)
    
    # Update price for next candle
    price = close_price
    
    # Create candlestick data structure (Hyperliquid format)
    candle = {
        "t": t,           # Open timestamp
        "T": T,           # Close timestamp
        "s": "ETH",       # Symbol
        "i": "15m",       # Interval
        "o": str(open_price),   # Open price
        "c": str(close_price),  # Close price
        "h": str(high_price),   # High price
        "l": str(low_price),    # Low price
        "v": str(volume),       # Volume
        "n": trades             # Number of trades
    }
    
    candles.append(candle)
    
    # Progress indicator
    if (i + 1) % 1000 == 0:
        print(f"Generated {i + 1}/{num_candles} candles...")

# Save data to file
output_file = "ETH-PERP-1m.json"
with open(output_file, "w") as f:
    json.dump(candles, f, indent=2)

print(f"\n✅ Successfully generated {num_candles} ETH candles!")
print(f"📁 Output file: {output_file}")
print(f"📊 Data points: {len(candles)}")
print(f"💰 Price range: ${min(float(c['l']) for c in candles):.2f} - ${max(float(c['h']) for c in candles):.2f}")
print(f"📈 Final price: ${float(candles[-1]['c']):.2f}")
print(f"🕐 Time range: {candles[0]['t']} - {candles[-1]['T']}")
print("\n🚀 Ready for backtesting!")