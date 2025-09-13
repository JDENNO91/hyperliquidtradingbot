"""
Live Trading CLI

This module provides a unified command-line interface for live trading execution,
allowing users to run strategies with real market data and execute actual trades.
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config.config_manager import ConfigManager

def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """Set up logging configuration."""
    logger = logging.getLogger("trade")
    logger.setLevel(getattr(logging, level.upper()))
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def trade_cli():
    """Main live trading CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Hyperliquid Trading Bot - Live Trading Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start live trading with default ETH configuration
  python -m src.cli.trade --profile live_eth
  
  # Live trading with custom parameters
  python -m src.cli.trade --profile live_btc --timeframe 15m --leverage 10
  
  # Live trading with specific start time
  python -m src.cli.trade --profile live_eth --start-time "2024-01-01 00:00:00"
  
  # Live trading with custom log file
  python -m src.cli.trade --profile live_eth --log-file live_trading.log
  
  # Dry run mode (no real trades)
  python -m src.cli.trade --profile live_eth --dry-run
        """
    )
    
    # Configuration options
    parser.add_argument(
        "--profile", "-p",
        default="live_eth",
        help="Configuration profile to use for live trading (default: live_eth)"
    )
    
    parser.add_argument(
        "--fallback", "-f",
        help="Fallback configuration profile"
    )
    
    # Trading parameters
    parser.add_argument(
        "--market", "-m",
        help="Market to trade (e.g., ETH-PERP, BTC-PERP)"
    )
    
    parser.add_argument(
        "--timeframe", "-t",
        help="Timeframe to use (e.g., 1m, 15m, 1h, 4h)"
    )
    
    parser.add_argument(
        "--leverage", "-l",
        type=float,
        help="Leverage to use for trading"
    )
    
    parser.add_argument(
        "--position-size", "-s",
        type=float,
        help="Position size as a decimal (0.0 to 1.0)"
    )
    
    parser.add_argument(
        "--capital", "-c",
        type=float,
        help="Initial capital for trading"
    )
    
    # Trading options
    parser.add_argument(
        "--start-time",
        help="Start time for trading (YYYY-MM-DD HH:MM:SS)"
    )
    
    parser.add_argument(
        "--end-time",
        help="End time for trading (YYYY-MM-DD HH:MM:SS)"
    )
    
    parser.add_argument(
        "--duration",
        help="Duration to run trading (e.g., 1h, 4h, 1d)"
    )
    
    parser.add_argument(
        "--max-trades",
        type=int,
        help="Maximum number of trades to execute"
    )
    
    # Safety options
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode (no real trades executed)"
    )
    
    parser.add_argument(
        "--confirm-trades",
        action="store_true",
        help="Require manual confirmation before each trade"
    )
    
    parser.add_argument(
        "--max-daily-loss",
        type=float,
        help="Maximum daily loss limit as percentage (0.0 to 1.0)"
    )
    
    # Output options
    parser.add_argument(
        "--output", "-o",
        help="Output file for trading results (JSON format)"
    )
    
    parser.add_argument(
        "--log-file",
        help="Log file for trading logging"
    )
    
    # Logging options
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress all output except errors"
    )
    
    # Risk management options
    parser.add_argument(
        "--max-risk-per-trade",
        type=float,
        help="Maximum risk per trade as percentage (0.0 to 1.0)"
    )
    
    parser.add_argument(
        "--max-drawdown",
        type=float,
        help="Maximum allowed drawdown as percentage (0.0 to 1.0)"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set up logging
    log_level = "DEBUG" if args.verbose else "INFO"
    if args.quiet:
        log_level = "ERROR"
    
    logger = setup_logging(log_level, args.log_file)
    
    try:
        # Initialize configuration manager
        config_manager = ConfigManager(logger=logger)
        
        # Load configuration
        logger.info(f"Loading configuration profile: {args.profile}")
        config = config_manager.load_config(args.profile, args.fallback)
        
        # Override config with command line arguments
        if args.market:
            config['trading']['market'] = args.market
            logger.info(f"Market overridden to: {args.market}")
        
        if args.timeframe:
            config['trading']['timeframe'] = args.timeframe
            logger.info(f"Timeframe overridden to: {args.timeframe}")
        
        if args.leverage:
            config['trading']['leverage'] = args.leverage
            logger.info(f"Leverage overridden to: {args.leverage}")
        
        if args.position_size:
            config['trading']['positionSize'] = args.position_size
            logger.info(f"Position size overridden to: {args.position_size}")
        
        if args.capital:
            config['trading']['initial_capital'] = args.capital
            logger.info(f"Initial capital overridden to: {args.capital}")
        
        if args.max_risk_per_trade:
            config['risk']['max_risk_per_trade'] = args.max_risk_per_trade
            logger.info(f"Max risk per trade overridden to: {args.max_risk_per_trade}")
        
        if args.max_drawdown:
            config['risk']['max_drawdown'] = args.max_drawdown
            logger.info(f"Max drawdown overridden to: {args.max_drawdown}")
        
        # Validate configuration
        is_valid, errors = config_manager.validate_config(config)
        if not is_valid:
            logger.error("Configuration validation failed:")
            for error in errors:
                logger.error(f"  - {error}")
            sys.exit(1)
        
        # Display configuration summary
        if not args.quiet:
            summary = config_manager.get_config_summary(args.profile)
            logger.info("Live Trading Configuration:")
            logger.info(f"  Market: {summary['trading']['market']}")
            logger.info(f"  Timeframe: {summary['trading']['timeframe']}")
            logger.info(f"  Leverage: {summary['trading']['leverage']}")
            logger.info(f"  Position Size: {summary['trading']['position_size']}")
            logger.info(f"  RSI Period: {summary['indicators']['rsi_period']}")
            logger.info(f"  BB Period: {summary['indicators']['bb_period']}")
            logger.info(f"  ADX Period: {summary['indicators']['adx_period']}")
            logger.info(f"  Max Risk per Trade: {summary['risk']['max_risk_per_trade']}")
            logger.info(f"  Max Drawdown: {summary['risk']['max_drawdown']}")
        
        # Display trading parameters
        if not args.quiet:
            logger.info("Trading Parameters:")
            if args.start_time:
                logger.info(f"  Start Time: {args.start_time}")
            if args.end_time:
                logger.info(f"  End Time: {args.end_time}")
            if args.duration:
                logger.info(f"  Duration: {args.duration}")
            if args.max_trades:
                logger.info(f"  Max Trades: {args.max_trades}")
            if args.dry_run:
                logger.info("  Mode: DRY RUN (no real trades)")
            if args.confirm_trades:
                logger.info("  Trade Confirmation: REQUIRED")
            if args.max_daily_loss:
                logger.info(f"  Max Daily Loss: {args.max_daily_loss:.1%}")
        
        # Safety warnings for live trading
        if not args.dry_run:
            logger.warning("=" * 60)
            logger.warning("⚠️  LIVE TRADING MODE - REAL MONEY AT RISK ⚠️")
            logger.warning("=" * 60)
            logger.warning("This will execute real trades with real money!")
            logger.warning("Ensure you have reviewed your configuration and risk settings.")
            logger.warning("Press Ctrl+C to cancel or any key to continue...")
            
            try:
                input()
            except KeyboardInterrupt:
                logger.info("Live trading cancelled by user")
                sys.exit(0)
        
        # TODO: Implement actual live trading logic
        # This would integrate with the existing live trading functionality
        logger.info("Starting live trading...")
        
        # Placeholder for trading results
        trading_results = {
            'profile': args.profile,
            'start_time': args.start_time or 'now',
            'end_time': args.end_time or 'ongoing',
            'duration': args.duration or 'unlimited',
            'max_trades': args.max_trades or 'unlimited',
            'dry_run': args.dry_run,
            'confirm_trades': args.confirm_trades,
            'status': 'not_implemented',
            'message': 'Live trading functionality will be implemented in the next phase'
        }
        
        # Save results to file if specified
        if args.output:
            try:
                import json
                with open(args.output, 'w') as f:
                    json.dump(trading_results, f, indent=2)
                logger.info(f"Trading results saved to: {args.output}")
            except Exception as e:
                logger.error(f"Failed to save results to {args.output}: {e}")
        
        logger.info("Live trading started!")
        logger.info("Note: Full live trading functionality will be implemented in the next phase")
        
        # TODO: Start actual live trading loop here
        
    except KeyboardInterrupt:
        logger.info("Live trading interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Live trading failed: {e}")
        if args.verbose:
            import traceback
            logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    trade_cli()
