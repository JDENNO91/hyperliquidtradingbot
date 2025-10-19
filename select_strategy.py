#!/usr/bin/env python3
"""
Simple Strategy Selector

Quick way to choose and run profitable production strategies.
"""

import sys
import subprocess
from pathlib import Path

STRATEGIES = {
    "1": {
        "name": "RSI Scalping Standard 5m",
        "config": "src/config/production/rsi_scalping/standard_5m.json",
        "trades_per_day": 2.3,
        "return": "97.06%",
        "drawdown": "2.94%",
        "description": "🏆 BEST - Highest returns, lowest risk"
    },
    "2": {
        "name": "RSI Scalping Extreme 5m",
        "config": "src/config/production/rsi_scalping/extreme_5m.json",
        "trades_per_day": 3.6,
        "return": "94.69%",
        "drawdown": "5.31%",
        "description": "⚡ ACTIVE - More trades, great returns"
    },
    "3": {
        "name": "MA+RSI Hybrid 5m",
        "config": "src/config/production/ma_rsi_hybrid/standard_5m.json",
        "trades_per_day": 1.4,
        "return": "96.47%",
        "drawdown": "3.53%",
        "description": "🎯 BALANCED - Highest win rate (10%)"
    },
    "4": {
        "name": "RSI Scalping Ultra 1m",
        "config": "src/config/production/rsi_scalping/ultra_1m.json",
        "trades_per_day": 44,
        "return": "46.60%",
        "drawdown": "53.40%",
        "description": "⚠️ HIGH FREQUENCY - 10+ trades/day but high risk"
    }
}

def print_header():
    print()
    print("╔" + "="*77 + "╗")
    print("║" + " "*21 + "🏆 PRODUCTION STRATEGY SELECTOR 🏆" + " "*22 + "║")
    print("╚" + "="*77 + "╝")
    print()

def print_strategies():
    print("Available Strategies (All Profitable on ETH-PERP):")
    print()
    
    for num, strategy in STRATEGIES.items():
        print(f"{num}. {strategy['name']}")
        print(f"   {strategy['description']}")
        print(f"   📊 {strategy['trades_per_day']} trades/day | {strategy['return']} return | {strategy['drawdown']} max DD")
        print()

def run_strategy(choice):
    if choice not in STRATEGIES:
        print(f"❌ Invalid choice: {choice}")
        return
    
    strategy = STRATEGIES[choice]
    config_path = strategy['config']
    
    print()
    print("━" * 79)
    print(f"Running: {strategy['name']}")
    print(f"Config: {config_path}")
    print("━" * 79)
    print()
    
    # Run backtest
    cmd = ["python3", "src/cli/backtest.py", "--config", config_path]
    result = subprocess.run(cmd)
    
    return result.returncode == 0

def main():
    print_header()
    print_strategies()
    
    print("━" * 79)
    choice = input("Select strategy (1-4) or 'q' to quit: ").strip()
    
    if choice.lower() == 'q':
        print("👋 Goodbye!")
        sys.exit(0)
    
    if choice in STRATEGIES:
        success = run_strategy(choice)
        if success:
            print()
            print("✅ Backtest completed!")
        else:
            print()
            print("❌ Backtest failed!")
    else:
        print(f"❌ Invalid choice: {choice}")
        print("Please choose 1-4")

if __name__ == "__main__":
    main()

