#!/usr/bin/env python3
"""
Timeframe Switcher CLI

A command-line tool for easily switching between different timeframes
and testing timeframe-specific strategies.
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from strategies.strategy_factory import StrategyFactory

class TimeframeSwitcher:
    """Timeframe switcher for trading strategies."""
    
    def __init__(self):
        self.available_timeframes = ['1m', '5m', '15m']
        self.available_strategies = {
            '1m': ['super_optimized'],
            '5m': ['super_optimized_5m'],
            '15m': ['super_optimized_15m']
        }
        self.config_templates = {
            '1m': 'timeframe_optimized/backtest_super_optimized_eth.json',
            '5m': 'timeframe_optimized/backtest_super_optimized_5m_eth.json',
            '15m': 'timeframe_optimized/backtest_super_optimized_15m_eth.json'
        }
    
    def list_timeframes(self):
        """List all available timeframes."""
        print("🕐 Available Timeframes:")
        print("=" * 50)
        for timeframe in self.available_timeframes:
            strategies = self.available_strategies[timeframe]
            print(f"📊 {timeframe.upper()}:")
            for strategy in strategies:
                print(f"   • {strategy}")
            print()
    
    def list_strategies(self, timeframe: str = None):
        """List all available strategies for a timeframe."""
        if timeframe:
            if timeframe not in self.available_timeframes:
                print(f"❌ Error: Timeframe '{timeframe}' not available")
                return
            
            strategies = self.available_strategies[timeframe]
            print(f"📊 Strategies for {timeframe.upper()} timeframe:")
            print("=" * 50)
            for strategy in strategies:
                print(f"   • {strategy}")
        else:
            print("📊 All Available Strategies:")
            print("=" * 50)
            for timeframe, strategies in self.available_strategies.items():
                print(f"🕐 {timeframe.upper()}:")
                for strategy in strategies:
                    print(f"   • {strategy}")
                print()
    
    def compare_timeframes(self):
        """Compare performance across timeframes."""
        print("📊 Timeframe Comparison:")
        print("=" * 80)
        print(f"{'Timeframe':<10} {'Hold Time':<12} {'Profit Target':<15} {'Position Size':<15} {'Strategy':<20}")
        print("-" * 80)
        
        comparisons = [
            ('1m', '10-20s', '1.2-2.0%', '40-60%', 'super_optimized'),
            ('5m', '60s', '2.5%', '45%', 'super_optimized_5m'),
            ('15m', '180s', '3.5%', '50%', 'super_optimized_15m')
        ]
        
        for timeframe, hold_time, profit_target, position_size, strategy in comparisons:
            print(f"{timeframe:<10} {hold_time:<12} {profit_target:<15} {position_size:<15} {strategy:<20}")
    
    def generate_config(self, timeframe: str, strategy: str = None, output_file: str = None):
        """Generate configuration file for a specific timeframe."""
        if timeframe not in self.available_timeframes:
            print(f"❌ Error: Timeframe '{timeframe}' not available")
            return
        
        if not strategy:
            strategy = self.available_strategies[timeframe][0]  # Use first available strategy
        
        if strategy not in self.available_strategies[timeframe]:
            print(f"❌ Error: Strategy '{strategy}' not available for {timeframe} timeframe")
            return
        
        # Load template config
        template_file = self.config_templates[timeframe]
        template_path = Path(__file__).parent.parent / 'config' / template_file
        
        if not template_path.exists():
            print(f"❌ Error: Template config file not found: {template_path}")
            return
        
        with open(template_path, 'r') as f:
            config = json.load(f)
        
        # Update strategy
        config['strategy'] = strategy
        
        # Update timeframe-specific parameters
        if timeframe == '5m':
            config['trading']['timeframe'] = '5m'
            config['trading']['positionSize'] = 0.45
            config['trading']['profitTarget'] = 0.025
            config['trading']['stop_loss_pct'] = 0.008
            config['trading']['take_profit_pct'] = 0.025
        elif timeframe == '15m':
            config['trading']['timeframe'] = '15m'
            config['trading']['positionSize'] = 0.5
            config['trading']['profitTarget'] = 0.035
            config['trading']['stop_loss_pct'] = 0.012
            config['trading']['take_profit_pct'] = 0.035
        
        # Save config
        if not output_file:
            output_file = f"backtest_{strategy}_{timeframe}_eth.json"
        
        output_path = Path(__file__).parent.parent / 'config' / output_file
        
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Generated config file: {output_path}")
        print(f"📊 Timeframe: {timeframe}")
        print(f"🎯 Strategy: {strategy}")
        print(f"💰 Position Size: {config['trading']['positionSize']}")
        print(f"🎯 Profit Target: {config['trading']['profitTarget']}")
    
    def run_backtest(self, timeframe: str, strategy: str = None, config_file: str = None):
        """Run backtest for a specific timeframe and strategy."""
        if timeframe not in self.available_timeframes:
            print(f"❌ Error: Timeframe '{timeframe}' not available")
            return
        
        if not strategy:
            strategy = self.available_strategies[timeframe][0]
        
        if not config_file:
            config_file = f"backtest_{strategy}_{timeframe}_eth.json"
        
        config_path = Path(__file__).parent.parent / 'config' / config_file
        
        if not config_path.exists():
            print(f"❌ Error: Config file not found: {config_path}")
            print("💡 Generate config first with: --generate-config")
            return
        
        print(f"🚀 Running backtest for {timeframe} timeframe with {strategy} strategy...")
        print(f"📁 Config: {config_path}")
        
        # Run backtest
        import subprocess
        cmd = [
            'python3', 
            'src/cli/improved_backtest.py',
            '--config', str(config_path),
            '--log-level', 'WARNING'
        ]
        
        try:
            result = subprocess.run(cmd, cwd=Path(__file__).parent.parent.parent, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
        except Exception as e:
            print(f"❌ Error running backtest: {e}")
    
    def show_help(self):
        """Show help information."""
        print("🕐 Timeframe Switcher Help:")
        print("=" * 50)
        print("This tool helps you switch between different timeframes and test")
        print("timeframe-specific strategies.")
        print()
        print("Available Commands:")
        print("  --list-timeframes     List all available timeframes")
        print("  --list-strategies     List all available strategies")
        print("  --compare-timeframes  Compare timeframes side by side")
        print("  --generate-config     Generate config for timeframe")
        print("  --run-backtest        Run backtest for timeframe")
        print()
        print("Examples:")
        print("  python timeframe_switcher.py --list-timeframes")
        print("  python timeframe_switcher.py --list-strategies 5m")
        print("  python timeframe_switcher.py --compare-timeframes")
        print("  python timeframe_switcher.py --generate-config 5m super_optimized_5m")
        print("  python timeframe_switcher.py --run-backtest 5m super_optimized_5m")

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description='Timeframe Switcher for Trading Strategies')
    
    # Action arguments
    parser.add_argument('--list-timeframes', action='store_true', help='List all available timeframes')
    parser.add_argument('--list-strategies', type=str, nargs='?', const='all', help='List strategies for timeframe (or all)')
    parser.add_argument('--compare-timeframes', action='store_true', help='Compare timeframes side by side')
    parser.add_argument('--generate-config', type=str, help='Generate config for timeframe')
    parser.add_argument('--run-backtest', type=str, help='Run backtest for timeframe')
    
    # Optional arguments
    parser.add_argument('--strategy', type=str, help='Strategy name')
    parser.add_argument('--config-file', type=str, help='Config file name')
    parser.add_argument('--output-file', type=str, help='Output file name')
    
    args = parser.parse_args()
    
    switcher = TimeframeSwitcher()
    
    if args.list_timeframes:
        switcher.list_timeframes()
    elif args.list_strategies is not None:
        if args.list_strategies == 'all':
            switcher.list_strategies()
        else:
            switcher.list_strategies(args.list_strategies)
    elif args.compare_timeframes:
        switcher.compare_timeframes()
    elif args.generate_config:
        switcher.generate_config(args.generate_config, args.strategy, args.output_file)
    elif args.run_backtest:
        switcher.run_backtest(args.run_backtest, args.strategy, args.config_file)
    else:
        switcher.show_help()

if __name__ == '__main__':
    main()
