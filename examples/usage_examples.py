"""
Comprehensive Usage Examples for Hyperliquid Python Trading Bot

This file demonstrates how to use all the major features of the trading system.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config.validator import validate_config_file, ConfigValidator
from utils.enhanced_logger import get_logger, setup_enhanced_logging
from utils.error_handler import get_error_handler, ErrorContext, TradingError, ErrorSeverity
from utils.error_handler import error_handler as error_handler_decorator
from strategies.optimization.genetic_optimizer import create_bb_rsi_optimizer, create_scalping_optimizer
from backtesting.improved_backtester import ImprovedBacktester
import json


def example_1_basic_logging():
    """Example 1: Basic logging setup and usage."""
    print("\n=== Example 1: Basic Logging ===")
    
    # Setup enhanced logging
    logger = setup_enhanced_logging("INFO", "logs")
    
    # Set context for structured logging
    logger.set_context(
        strategy="BBRSI",
        market="ETH-PERP",
        trade_id="12345",
        session_id="session_001"
    )
    
    # Log different types of messages
    logger.info("Starting trading session")
    logger.debug("Strategy parameters loaded")
    logger.warning("High volatility detected")
    
    # Log trade data
    trade_data = {
        'action': 'BUY',
        'market': 'ETH-PERP',
        'price': 2500.0,
        'size': 0.1,
        'pnl': 25.0,
        'duration': 30
    }
    logger.log_trade(trade_data)
    
    # Log performance metrics
    logger.log_performance("sharpe_ratio", 1.85)
    logger.log_performance("max_drawdown", -0.05)
    
    print("✅ Logging example completed")


def example_2_config_validation():
    """Example 2: Configuration validation."""
    print("\n=== Example 2: Configuration Validation ===")
    
    # Create a test configuration
    test_config = {
        "strategy": "bbrsi",
        "trading": {
            "market": "ETH-PERP",
            "positionSize": 0.1,
            "leverage": 5,
            "timeframe": "1m"
        },
        "indicators": {
            "rsi": {
                "period": 14,
                "overbought": 70,
                "oversold": 30
            },
            "bollinger": {
                "period": 20,
                "stdDev": 2
            },
            "adx": {
                "period": 14,
                "threshold": 20
            }
        }
    }
    
    # Validate configuration
    validator = ConfigValidator()
    is_valid, issues = validator.validate(test_config)
    
    print(f"Configuration valid: {is_valid}")
    if issues:
        print("Issues found:")
        for issue in issues:
            print(f"  - {issue.field}: {issue.message}")
    else:
        print("✅ Configuration is valid!")
    
    # Test invalid configuration
    invalid_config = {
        "strategy": "invalid_strategy",
        "trading": {
            "market": "INVALID-MARKET",
            "positionSize": -0.1,  # Invalid negative value
            "leverage": 0,  # Invalid zero leverage
        }
    }
    
    is_valid, issues = validator.validate(invalid_config)
    print(f"\nInvalid configuration valid: {is_valid}")
    print("Issues found:")
    for issue in issues:
        print(f"  - {issue.field}: {issue.message}")


def example_3_error_handling():
    """Example 3: Error handling and recovery."""
    print("\n=== Example 3: Error Handling ===")
    
    # Get error handler
    error_handler = get_error_handler()
    
    # Create error context
    context = ErrorContext(
        component="trading_engine",
        operation="execute_trade",
        trade_id="12345"
    )
    
    # Example of handling different types of errors
    try:
        # Simulate a trading error
        raise TradingError("Insufficient balance for trade", ErrorSeverity.HIGH, context)
    except TradingError as e:
        success = error_handler.handle_error(e, context)
        print(f"Error handled successfully: {success}")
    
    # Example with error handler decorator
    @error_handler_decorator("strategy", "calculate_signal")
    def risky_calculation(x):
        if x < 0:
            raise TradingError("Negative value not allowed", ErrorSeverity.MEDIUM)
        return x * 2
    
    # Test the decorated function
    result = risky_calculation(5)
    print(f"Safe calculation result: {result}")
    
    # This will be handled by the decorator
    try:
        result = risky_calculation(-1)
        print(f"Error handled by decorator: {result}")
    except TradingError as e:
        print(f"Error caught and handled: {e}")
        result = None


def example_4_strategy_optimization():
    """Example 4: Strategy optimization with genetic algorithms."""
    print("\n=== Example 4: Strategy Optimization ===")
    
    # Create BBRSI optimizer
    optimizer = create_bb_rsi_optimizer()
    
    # Define a simple fitness function (in real usage, this would run backtests)
    def mock_fitness(parameters):
        # Mock fitness calculation based on parameter values
        rsi_period = parameters.get('rsi_period', 14)
        bollinger_std = parameters.get('bollinger_std', 2.0)
        
        # Simple fitness: prefer certain parameter ranges
        fitness = 0.5
        if 10 <= rsi_period <= 20:
            fitness += 0.2
        if 1.5 <= bollinger_std <= 2.5:
            fitness += 0.3
        
        return fitness
    
    # Set fitness function
    optimizer.set_fitness_function(mock_fitness)
    
    print("Running genetic optimization...")
    result = optimizer.optimize()
    
    print(f"Best parameters: {result.best_parameters}")
    print(f"Best fitness: {result.best_fitness:.4f}")
    print(f"Generations: {result.generation}")
    print(f"Converged at generation: {result.convergence_generation}")
    
    # Save results
    optimizer.save_results(result, "optimization_results.json")
    print("✅ Optimization results saved")


def example_5_backtesting():
    """Example 5: Running backtests."""
    print("\n=== Example 5: Backtesting ===")
    
    # Create a test configuration
    config = {
        "strategy": "bbrsi",
        "trading": {
            "market": "ETH-PERP",
            "positionSize": 0.1,
            "leverage": 5,
            "timeframe": "1m"
        },
        "indicators": {
            "rsi": {
                "period": 14,
                "overbought": 70,
                "oversold": 30
            },
            "bollinger": {
                "period": 20,
                "stdDev": 2
            },
            "adx": {
                "period": 14,
                "threshold": 20
            }
        },
        "backtest": {
            "initialCapital": 10000,
            "tradingFee": 0.001,
            "slippage": 0.0005
        }
    }
    
    # Create mock data
    mock_data = [
        {
            "t": 1640995200000 + i * 60000,  # 1 minute intervals
            "o": 100 + i * 0.1,
            "h": 105 + i * 0.1,
            "l": 95 + i * 0.1,
            "c": 102 + i * 0.1,
            "v": 1000 + i * 10
        }
        for i in range(1000)  # 1000 data points
    ]
    
    # Save config and data to temporary files
    config_path = "temp_config.json"
    data_path = "temp_data.json"
    
    with open(config_path, 'w') as f:
        json.dump(config, f)
    
    with open(data_path, 'w') as f:
        json.dump(mock_data, f)
    
    try:
        # Create backtester
        backtester = ImprovedBacktester(config_path)
        
        # Run backtest (this would normally load real data)
        print("Running backtest...")
        # Note: In a real scenario, you would call backtester.run() with actual data
        
        print("✅ Backtesting example completed")
        
    finally:
        # Clean up temporary files
        if os.path.exists(config_path):
            os.remove(config_path)
        if os.path.exists(data_path):
            os.remove(data_path)


def example_6_performance_monitoring():
    """Example 6: Performance monitoring and metrics."""
    print("\n=== Example 6: Performance Monitoring ===")
    
    # Setup logger with performance monitoring
    logger = setup_enhanced_logging("INFO", "logs")
    
    # Simulate trading session with performance metrics
    logger.set_context(strategy="BBRSI", market="ETH-PERP")
    
    # Log various performance metrics
    metrics = [
        ("sharpe_ratio", 1.85),
        ("max_drawdown", -0.05),
        ("win_rate", 0.65),
        ("profit_factor", 1.8),
        ("total_trades", 150),
        ("avg_trade_duration", 45.5),
        ("consecutive_wins", 8),
        ("consecutive_losses", 3)
    ]
    
    for metric_name, value in metrics:
        logger.log_performance(metric_name, value)
    
    # Get metrics summary
    metrics_summary = logger.get_metrics_summary()
    print("Performance Metrics Summary:")
    for metric, data in metrics_summary.items():
        print(f"  {metric}: {data['value']} (at {data['timestamp']})")
    
    print("✅ Performance monitoring example completed")


def example_7_market_data_generation():
    """Example 7: Market data generation for additional cryptocurrencies."""
    print("\n=== Example 7: Market Data Generation ===")
    
    from backtesting.data.generate_market_data import generate_candles
    
    # Generate data for different cryptocurrencies
    symbols = ['SOL-PERP', 'AVAX-PERP', 'MATIC-PERP']
    base_prices = {'SOL-PERP': 50, 'AVAX-PERP': 25, 'MATIC-PERP': 0.8}
    
    for symbol in symbols:
        print(f"Generating data for {symbol}...")
        candles = generate_candles(
            symbol=symbol,
            timeframe=1,  # 1 minute
            days=7,  # 7 days of data
            base_price=base_prices[symbol]
        )
        
        print(f"  Generated {len(candles)} candles")
        print(f"  Price range: ${candles[0]['c']:.2f} - ${candles[-1]['c']:.2f}")
        print(f"  Volume range: {min(c['v'] for c in candles)} - {max(c['v'] for c in candles)}")
    
    print("✅ Market data generation example completed")


def main():
    """Run all examples."""
    print("🚀 Hyperliquid Python Trading Bot - Usage Examples")
    print("=" * 60)
    
    try:
        example_1_basic_logging()
        example_2_config_validation()
        example_3_error_handling()
        example_4_strategy_optimization()
        example_5_backtesting()
        example_6_performance_monitoring()
        example_7_market_data_generation()
        
        print("\n🎉 All examples completed successfully!")
        print("\nNext steps:")
        print("1. Run backtests: python -m cli.backtest --config config/core/backtest_eth.json")
        print("2. Start live simulation: python -m cli.simulate --profile live_eth --strategy bbrsi")
        print("3. View dashboard: streamlit run src/application/dashboard.py")
        print("4. Run tests: python -m pytest tests/ -v")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
