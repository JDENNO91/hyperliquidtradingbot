"""
Strategy Optimization CLI

This module provides a unified command-line interface for strategy optimization,
consolidating the previous separate optimization scripts into one consistent interface.
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Optional, List

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config.config_manager import ConfigManager

def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """Set up logging configuration."""
    logger = logging.getLogger("optimize")
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

def optimize_cli():
    """Main optimization CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Hyperliquid Trading Bot - Strategy Optimization Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Optimize ETH strategy with default parameters
  python -m src.cli.optimize --profile backtest_eth
  
  # Optimize with specific metric focus
  python -m src.cli.optimize --profile backtest_btc --metric sharpe_ratio
  
  # Custom parameter ranges
  python -m src.cli.optimize --profile backtest_eth --rsi-periods 10,14,20 --bb-stddev 1.5,2.0,2.5
  
  # Save optimization results
  python -m src.cli.optimize --profile backtest_eth --output optimization_results.json
        """
    )
    
    # Configuration options
    parser.add_argument(
        "--profile", "-p",
        default="backtest_eth",
        help="Configuration profile to use for optimization (default: backtest_eth)"
    )
    
    # Optimization parameters
    parser.add_argument(
        "--metric", "-m",
        default="sharpe_ratio",
        choices=["sharpe_ratio", "profit_factor", "win_rate", "max_drawdown", "net_profit"],
        help="Metric to optimize for (default: sharpe_ratio)"
    )
    
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=100,
        help="Maximum number of optimization iterations (default: 100)"
    )
    
    parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        help="Number of parallel optimization processes (default: 1)"
    )
    
    # Parameter ranges
    parser.add_argument(
        "--rsi-periods",
        help="RSI periods to test (comma-separated, e.g., 10,14,20)"
    )
    
    parser.add_argument(
        "--rsi-overbought",
        help="RSI overbought levels to test (comma-separated, e.g., 65,70,75)"
    )
    
    parser.add_argument(
        "--rsi-oversold",
        help="RSI oversold levels to test (comma-separated, e.g., 25,30,35)"
    )
    
    parser.add_argument(
        "--bb-periods",
        help="Bollinger Band periods to test (comma-separated, e.g., 15,20,25)"
    )
    
    parser.add_argument(
        "--bb-stddev",
        help="Bollinger Band standard deviations to test (comma-separated, e.g., 1.5,2.0,2.5)"
    )
    
    parser.add_argument(
        "--adx-periods",
        help="ADX periods to test (comma-separated, e.g., 10,14,20)"
    )
    
    parser.add_argument(
        "--adx-thresholds",
        help="ADX thresholds to test (comma-separated, e.g., 15,20,25)"
    )
    
    parser.add_argument(
        "--leverage-levels",
        help="Leverage levels to test (comma-separated, e.g., 3,5,10)"
    )
    
    parser.add_argument(
        "--position-sizes",
        help="Position sizes to test (comma-separated, e.g., 0.05,0.1,0.2)"
    )
    
    # Output options
    parser.add_argument(
        "--output", "-o",
        help="Output file for optimization results (JSON format)"
    )
    
    parser.add_argument(
        "--results-dir",
        default="optimization_results",
        help="Directory to save detailed optimization results (default: optimization_results)"
    )
    
    parser.add_argument(
        "--log-file",
        help="Log file for optimization logging"
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
        
        # Load base configuration
        logger.info(f"Loading configuration profile: {args.profile}")
        base_config = config_manager.load_config(args.profile)
        
        # Parse parameter ranges
        parameter_ranges = {}
        
        if args.rsi_periods:
            parameter_ranges['rsi.period'] = [int(x.strip()) for x in args.rsi_periods.split(',')]
        
        if args.rsi_overbought:
            parameter_ranges['rsi.overbought'] = [float(x.strip()) for x in args.rsi_overbought.split(',')]
        
        if args.rsi_oversold:
            parameter_ranges['rsi.oversold'] = [float(x.strip()) for x in args.rsi_oversold.split(',')]
        
        if args.bb_periods:
            parameter_ranges['bollinger.period'] = [int(x.strip()) for x in args.bb_periods.split(',')]
        
        if args.bb_stddev:
            parameter_ranges['bollinger.stdDev'] = [float(x.strip()) for x in args.bb_stddev.split(',')]
        
        if args.adx_periods:
            parameter_ranges['adx.period'] = [int(x.strip()) for x in args.adx_periods.split(',')]
        
        if args.adx_thresholds:
            parameter_ranges['adx.threshold'] = [float(x.strip()) for x in args.adx_thresholds.split(',')]
        
        if args.leverage_levels:
            parameter_ranges['trading.leverage'] = [int(x.strip()) for x in args.leverage_levels.split(',')]
        
        if args.position_sizes:
            parameter_ranges['trading.positionSize'] = [float(x.strip()) for x in args.position_sizes.split(',')]
        
        # Use default parameter ranges if none specified
        if not parameter_ranges:
            parameter_ranges = {
                'rsi.period': [10, 14, 20],
                'rsi.overbought': [65, 70, 75],
                'rsi.oversold': [25, 30, 35],
                'bollinger.period': [15, 20, 25],
                'bollinger.stdDev': [1.5, 2.0, 2.5],
                'adx.period': [10, 14, 20],
                'adx.threshold': [15, 20, 25],
                'trading.leverage': [3, 5, 10],
                'trading.positionSize': [0.05, 0.1, 0.2]
            }
        
        # Display optimization parameters
        if not args.quiet:
            logger.info("Optimization Parameters:")
            logger.info(f"  Metric: {args.metric}")
            logger.info(f"  Max Iterations: {args.max_iterations}")
            logger.info(f"  Parallel Processes: {args.parallel}")
            logger.info("  Parameter Ranges:")
            for param, values in parameter_ranges.items():
                logger.info(f"    {param}: {values}")
        
        # TODO: Implement actual optimization logic
        # This would integrate with the existing optimize_strategy.py functionality
        logger.info("Starting optimization process...")
        
        # Placeholder for optimization results
        optimization_results = {
            'profile': args.profile,
            'metric': args.metric,
            'parameter_ranges': parameter_ranges,
            'max_iterations': args.max_iterations,
            'status': 'not_implemented',
            'message': 'Optimization functionality will be implemented in the next phase'
        }
        
        # Save results
        if args.output:
            try:
                import json
                with open(args.output, 'w') as f:
                    json.dump(optimization_results, f, indent=2)
                logger.info(f"Optimization results saved to: {args.output}")
            except Exception as e:
                logger.error(f"Failed to save results to {args.output}: {e}")
        
        # Create results directory
        results_dir = Path(args.results_dir)
        results_dir.mkdir(exist_ok=True)
        
        # Save detailed results
        detailed_results_path = results_dir / f"{args.profile}_optimization_{args.metric}.json"
        try:
            import json
            with open(detailed_results_path, 'w') as f:
                json.dump(optimization_results, f, indent=2)
            logger.info(f"Detailed results saved to: {detailed_results_path}")
        except Exception as e:
            logger.error(f"Failed to save detailed results: {e}")
        
        logger.info("Optimization process completed!")
        logger.info("Note: Full optimization functionality will be implemented in the next phase")
        
    except KeyboardInterrupt:
        logger.info("Optimization interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        if args.verbose:
            import traceback
            logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    optimize_cli()
