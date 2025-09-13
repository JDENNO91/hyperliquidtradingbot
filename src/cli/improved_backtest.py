#!/usr/bin/env python3
"""
Improved Backtest CLI

A command-line interface for running backtests with the improved backtesting system.
"""

import argparse
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backtesting.improved_backtester import ImprovedBacktester


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description='Improved Backtest CLI')
    
    # Required arguments
    parser.add_argument('--config', '-c', required=True, help='Configuration file path')
    
    # Optional arguments
    parser.add_argument('--data', '-d', help='Market data file path (overrides config)')
    parser.add_argument('--output', '-o', help='Output file for results')
    parser.add_argument('--log-level', default='INFO', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    parser.add_argument('--log-file', help='Log file path')
    parser.add_argument('--summary', action='store_true', help='Print summary only')
    
    args = parser.parse_args()
    
    try:
        # Create backtester
        backtester = ImprovedBacktester(
            config_path=args.config,
            log_level=args.log_level,
            log_file=args.log_file
        )
        
        # Determine data file
        data_file = args.data
        if not data_file:
            # Try to get from config
            data_file = backtester.config.get('data_file')
            if not data_file:
                print("Error: No data file specified. Use --data or set data_file in config.")
                sys.exit(1)
        
        # Check if data file exists
        if not Path(data_file).exists():
            print(f"Error: Data file not found: {data_file}")
            sys.exit(1)
        
        # Run backtest
        print(f"Running backtest with config: {args.config}")
        print(f"Data file: {data_file}")
        print()
        
        # Run the backtest
        import asyncio
        results = asyncio.run(backtester.run_backtest(data_file))
        
        # Print summary
        backtester.print_summary()
        
        # Save results if requested
        if args.output:
            backtester.save_results(args.output)
            print(f"\nResults saved to: {args.output}")
        
        # Print detailed results if not summary only
        if not args.summary and args.log_level == 'DEBUG':
            print("\nDetailed Results:")
            print(json.dumps(results, indent=2))
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
