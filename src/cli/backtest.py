"""
Unified CLI for Backtesting Operations

Clean command-line interface for running backtests using the unified system.
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backtesting.improved_backtester import ImprovedBacktester
from utils.logger import setup_logger

def setup_logging(log_level: str = "INFO", log_file: str = None):
    """Setup logging configuration."""
    setup_logger(name=__name__, level=log_level, log_file=log_file)

async def backtest_cli(config_path: str, data_path: str = None, output_file: str = None, 
                       log_level: str = "INFO", log_file: str = None):
    """Run backtest using the unified system."""
    # Setup logging
    setup_logging(log_level, log_file)
    logger = logging.getLogger(__name__)
    
    try:
        # Validate config file exists
        if not Path(config_path).exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        # Auto-detect data path if not provided
        if not data_path:
            data_path = _infer_data_path_from_config(config_path)
            if not data_path:
                raise ValueError("Data path not provided and could not be inferred from config")
        
        # Validate data file exists
        if not Path(data_path).exists():
            raise FileNotFoundError(f"Market data file not found: {data_path}")
        
        logger.info(f"Starting backtest with config: {config_path}")
        logger.info(f"Using market data: {data_path}")
        
        # Create and run backtester
        backtester = ImprovedBacktester(config_path, log_level)
        results = await backtester.run_backtest(data_path)
        
        # Display results
        print("\n" + "="*60)
        print(backtester.get_summary())
        print("="*60)
        
        if output_file:
            print(f"\nDetailed results saved to: {output_file}")
        
        return results
        
    except Exception as e:
        logger.error(f"Backtest failed: {e}")
        raise

def _infer_data_path_from_config(config_path: str) -> str:
    """Infer market data path from configuration file."""
    try:
        import json
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check for explicit data path
        data_path = config.get('data', {}).get('path')
        if data_path and Path(data_path).exists():
            return data_path
        
        # Infer from market and timeframe
        market = config.get('trading', {}).get('market', 'ETH-PERP')
        timeframe = config.get('trading', {}).get('timeframe', '1m')
        
        if market:
            # Try common data locations with fallbacks
            possible_paths = [
                # Standard project structure
                f"src/backtesting/data/{market}/{market}-{timeframe}.json",
                f"src/data/{market}/{market}-{timeframe}.json",
                f"data/{market}/{market}-{timeframe}.json",
                
                # Alternative timeframes
                f"src/backtesting/data/{market}/{market}-15m.json",
                f"src/backtesting/data/{market}/{market}-1m.json",
                f"src/backtesting/data/{market}/{market}-5m.json",
                f"src/backtesting/data/{market}/{market}-1h.json",
                
                # Root level data
                f"src/backtesting/data/{market}-{timeframe}.json",
                f"data/{market}-{timeframe}.json",
                
                # Legacy paths
                f"backtesting/data/{market}/{market}-{timeframe}.json",
                f"backtesting/data/{market}-{timeframe}.json"
            ]
            
            for path in possible_paths:
                if Path(path).exists():
                    return path
        
        return None
        
    except Exception as e:
        logging.warning(f"Failed to infer data path: {e}")
        return None

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="🚀 Unified Backtesting CLI - Run backtests with smart defaults",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🎯 **Examples:**

  # Run backtest with config and data files
  python -m cli.backtest --config config/backtest_eth.json --data data/ETH-PERP-1m.json
  
  # Run backtest with auto-detected data path (recommended)
  python -m cli.backtest --config config/backtest_eth.json
  
  # Save results to file
  python -m cli.backtest --config config/backtest_eth.json --output results.json
  
  # Verbose logging for debugging
  python -m cli.backtest --config config/backtest_eth.json --log-level DEBUG

📁 **Smart Data Detection:**
  The CLI automatically detects market data files based on your config.
  Just specify the config file and let it find the right data!
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        required=True,
        help='Configuration file path'
    )
    
    parser.add_argument(
        '--data', '-d',
        help='Market data file path (optional, will try to infer from config)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file to save results (optional)'
    )
    
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--log-file',
        help='Log file path (optional)'
    )
    
    args = parser.parse_args()
    
    try:
        # Run backtest
        asyncio.run(backtest_cli(
            config_path=args.config,
            data_path=args.data,
            output_file=args.output,
            log_level=args.log_level,
            log_file=args.log_file
        ))
        
    except KeyboardInterrupt:
        print("\nBacktest cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"Backtest failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
