#!/usr/bin/env python3
"""
Main entry point for the Hyperliquid Trading Bot CLI.

This module provides a unified command-line interface for all major functionalities.
"""

import sys
import argparse
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from cli import backtest_cli, optimize_cli, simulate_cli, trade_cli
from utils.logger import setup_logger

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Hyperliquid Trading Bot - Unified CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run backtest
  python src/main.py backtest --config config/backtest_eth.json
  
  # Optimize strategy parameters
  python src/main.py optimize --strategy bbrsi --metric sharpe
  
  # Run live simulation
  python src/main.py simulate --config config/simulation.json
  
  # Execute live trades (dry-run mode)
  python src/main.py trade --config config/live.json --dry-run
        """
    )
    
    parser.add_argument(
        'command',
        choices=['backtest', 'optimize', 'simulate', 'trade'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Configuration file path'
    )
    
    parser.add_argument(
        '--strategy',
        type=str,
        choices=['bbrsi', 'scalping'],
        help='Strategy to use (for optimization)'
    )
    
    parser.add_argument(
        '--metric',
        type=str,
        choices=['sharpe', 'profit', 'drawdown', 'winrate'],
        help='Optimization metric (for optimization)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run mode (for live trading)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        help='Log file path'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    if args.log_file:
        setup_logger(level=log_level, log_file=args.log_file)
    else:
        setup_logger(level=log_level)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Executing command: {args.command}")
    
    try:
        if args.command == 'backtest':
            if not args.config:
                logger.error("Backtest command requires --config argument")
                sys.exit(1)
            import asyncio
            asyncio.run(backtest_cli(args.config))
            
        elif args.command == 'optimize':
            if not args.strategy or not args.metric:
                logger.error("Optimize command requires --strategy and --metric arguments")
                sys.exit(1)
            # Note: optimize_cli() takes no parameters - uses sys.argv
            sys.argv = ['optimize', '--profile', args.config or 'backtest_eth', '--metric', args.metric]
            optimize_cli()
            
        elif args.command == 'simulate':
            if not args.config:
                logger.error("Simulate command requires --config argument")
                sys.exit(1)
            # Import and call the new simulation CLI
            from cli.simulate import simulate_cli
            # Set up sys.argv for the simulation CLI
            sys.argv = ['simulate', '--profile', args.config]
            simulate_cli()
            
        elif args.command == 'trade':
            if not args.config:
                logger.error("Trade command requires --config argument")
                sys.exit(1)
            # Note: trade_cli() takes no parameters - uses sys.argv
            sys.argv = ['trade', '--profile', args.config]
            if args.dry_run:
                sys.argv.append('--dry-run')
            trade_cli()
            
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error executing {args.command}: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
