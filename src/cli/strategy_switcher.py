#!/usr/bin/env python3
"""
Strategy Switcher CLI

A command-line tool for easy strategy switching and configuration management.
"""

import argparse
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.strategy_switcher import StrategySwitcher


def list_strategies():
    """List all available strategies."""
    switcher = StrategySwitcher()
    strategies = switcher.get_available_strategies()
    
    print("Available Trading Strategies:")
    print("=" * 50)
    
    for strategy in strategies:
        print(f"\n{strategy['id'].upper()}: {strategy['name']}")
        print(f"  Description: {strategy['description']}")
        print(f"  Risk Level: {strategy['risk_level']}")
        print(f"  Characteristics:")
        for key, value in strategy['characteristics'].items():
            print(f"    - {key.replace('_', ' ').title()}: {value}")


def compare_strategies(strategy_ids=None):
    """Compare multiple strategies."""
    switcher = StrategySwitcher()
    
    if strategy_ids is None:
        strategy_ids = ['bbrsi', 'scalping']
    
    comparison = switcher.compare_strategies(strategy_ids)
    
    print("Strategy Comparison:")
    print("=" * 50)
    
    for strategy_id, info in comparison.items():
        print(f"\n{strategy_id.upper()}: {info['name']}")
        print(f"  Risk Level: {info['risk_level']}")
        print(f"  Suitable For: {', '.join(info['suitable_for'])}")
        print(f"  Characteristics:")
        for key, value in info['characteristics'].items():
            print(f"    - {key.replace('_', ' ').title()}: {value}")


def get_recommendation(market_conditions, risk_tolerance):
    """Get strategy recommendation."""
    switcher = StrategySwitcher()
    recommendation = switcher.get_strategy_recommendation(market_conditions, risk_tolerance)
    
    print(f"Strategy Recommendation:")
    print(f"Market Conditions: {market_conditions}")
    print(f"Risk Tolerance: {risk_tolerance}")
    print(f"Recommended Strategy: {recommendation.upper()}")
    
    # Show why this strategy was recommended
    strategy_info = switcher.strategies[recommendation]
    print(f"\nWhy {strategy_info['name']}?")
    print(f"- Risk Level: {strategy_info['risk_level']}")
    print(f"- Characteristics: {strategy_info['characteristics']}")


def generate_config(strategy_id, mode='backtest', output_file=None, **kwargs):
    """Generate configuration for a strategy."""
    switcher = StrategySwitcher()
    
    if mode == 'backtest':
        config = switcher.create_backtest_config(strategy_id, **kwargs)
    elif mode == 'live':
        config = switcher.create_live_config(strategy_id, **kwargs)
    else:
        print(f"Error: Unknown mode '{mode}'. Use 'backtest' or 'live'.")
        return
    
    if output_file:
        switcher.save_config(strategy_id, config, output_file)
        print(f"Configuration saved to {output_file}")
    else:
        print(json.dumps(config, indent=2))


def run_backtest(strategy_id, **kwargs):
    """Run a backtest with the specified strategy."""
    import subprocess
    import tempfile
    import os
    
    switcher = StrategySwitcher()
    config = switcher.create_backtest_config(strategy_id, **kwargs)
    
    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f, indent=2)
        temp_config = f.name
    
    try:
        # Run backtest
        cmd = [
            sys.executable, 
            'src/cli/backtest.py',
            '--config', temp_config,
            '--log-level', 'WARNING'
        ]
        
        print(f"Running backtest for {strategy_id.upper()} strategy...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"Return code: {result.returncode}")
        
    finally:
        # Clean up temporary file
        os.unlink(temp_config)


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description='Strategy Switcher CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List strategies command
    subparsers.add_parser('list', help='List all available strategies')
    
    # Compare strategies command
    compare_parser = subparsers.add_parser('compare', help='Compare strategies')
    compare_parser.add_argument('strategies', nargs='*', default=['bbrsi', 'scalping'],
                               help='Strategy IDs to compare')
    
    # Get recommendation command
    recommend_parser = subparsers.add_parser('recommend', help='Get strategy recommendation')
    recommend_parser.add_argument('market', choices=['trending', 'ranging', 'volatile', 'low_volatility'],
                                 help='Market conditions')
    recommend_parser.add_argument('risk', choices=['low', 'medium', 'high'],
                                 help='Risk tolerance')
    
    # Generate config command
    config_parser = subparsers.add_parser('config', help='Generate strategy configuration')
    config_parser.add_argument('strategy', choices=['bbrsi', 'scalping'],
                              help='Strategy ID')
    config_parser.add_argument('--mode', choices=['backtest', 'live'], default='backtest',
                              help='Configuration mode')
    config_parser.add_argument('--output', '-o', help='Output file path')
    config_parser.add_argument('--symbol', default='ETH-PERP', help='Trading symbol')
    config_parser.add_argument('--capital', type=float, default=10000, help='Initial capital')
    config_parser.add_argument('--risk', type=float, default=0.02, help='Risk per trade')
    
    # Run backtest command
    backtest_parser = subparsers.add_parser('backtest', help='Run backtest with strategy')
    backtest_parser.add_argument('strategy', choices=['bbrsi', 'scalping'],
                                help='Strategy ID')
    backtest_parser.add_argument('--symbol', default='ETH-PERP', help='Trading symbol')
    backtest_parser.add_argument('--capital', type=float, default=10000, help='Initial capital')
    backtest_parser.add_argument('--risk', type=float, default=0.02, help='Risk per trade')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'list':
            list_strategies()
        
        elif args.command == 'compare':
            compare_strategies(args.strategies)
        
        elif args.command == 'recommend':
            get_recommendation(args.market, args.risk)
        
        elif args.command == 'config':
            kwargs = {
                'symbol': args.symbol,
                'initial_capital': args.capital,
                'risk_per_trade': args.risk
            }
            generate_config(args.strategy, args.mode, args.output, **kwargs)
        
        elif args.command == 'backtest':
            kwargs = {
                'symbol': args.symbol,
                'initial_capital': args.capital,
                'risk_per_trade': args.risk
            }
            run_backtest(args.strategy, **kwargs)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
