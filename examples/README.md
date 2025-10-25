# Usage Examples

This directory contains comprehensive examples demonstrating how to use all the major features of the Hyperliquid Python Trading Bot.

## Quick Start

Run all examples at once:

```bash
cd examples
python usage_examples.py
```

## Individual Examples

### 1. Basic Logging (`example_1_basic_logging`)
Demonstrates how to set up and use the enhanced logging system with structured logging, context management, and performance metrics.

**Key Features:**
- Structured logging with context
- Trade logging
- Performance metrics logging
- Multiple log levels

### 2. Configuration Validation (`example_2_config_validation`)
Shows how to validate trading configurations to ensure they're correct before running strategies.

**Key Features:**
- Configuration validation
- Error reporting
- Parameter range checking
- Business logic validation

### 3. Error Handling (`example_3_error_handling`)
Demonstrates the comprehensive error handling system with recovery mechanisms and circuit breakers.

**Key Features:**
- Error context management
- Automatic recovery strategies
- Circuit breaker patterns
- Decorator-based error handling

### 4. Strategy Optimization (`example_4_strategy_optimization`)
Shows how to use genetic algorithms to optimize trading strategy parameters.

**Key Features:**
- Genetic algorithm optimization
- Parameter range definition
- Fitness function implementation
- Results saving and analysis

### 5. Backtesting (`example_5_backtesting`)
Demonstrates how to run backtests with different strategies and configurations.

**Key Features:**
- Configuration-based backtesting
- Mock data generation
- Performance analysis
- Results export

### 6. Performance Monitoring (`example_6_performance_monitoring`)
Shows how to monitor and log performance metrics during trading.

**Key Features:**
- Real-time metrics logging
- Performance summaries
- Trade statistics
- Risk metrics

### 7. Market Data Generation (`example_7_market_data_generation`)
Demonstrates how to generate realistic market data for additional cryptocurrencies.

**Key Features:**
- Multi-symbol data generation
- Realistic price movements
- Volume simulation
- Timeframe flexibility

## Advanced Usage

### Custom Strategy Development

```python
from strategies.core.base_strategy import BaseStrategy

class MyCustomStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        self.name = "MyCustomStrategy"
    
    def compute_indicators(self, data, index):
        # Your indicator calculations
        return indicators
    
    def generate_signal(self, data, index):
        # Your signal generation logic
        return signal
```

### Custom Error Recovery

```python
from utils.error_handler import ErrorHandler, ErrorContext

def custom_recovery_strategy(error, context):
    # Your custom recovery logic
    return True

handler = ErrorHandler()
handler.recovery_strategies['my_error_type'] = custom_recovery_strategy
```

### Custom Performance Metrics

```python
from utils.enhanced_logger import get_logger

logger = get_logger()
logger.log_performance("custom_metric", value)
```

## Integration Examples

### With Streamlit Dashboard

```python
import streamlit as st
from application.dashboard import TradingDashboard

# Create dashboard instance
dashboard = TradingDashboard(mode="live_simulation")
dashboard.run()
```

### With Docker

```bash
# Build and run with Docker
docker build -t hyperliquid-trading-bot .
docker run -p 8501:8501 hyperliquid-trading-bot
```

### With GitHub Actions

The project includes pre-configured GitHub Actions workflows for:
- Automated testing
- Security scanning
- Docker builds
- Deployment

## Best Practices

1. **Always validate configurations** before running strategies
2. **Use structured logging** for better debugging and monitoring
3. **Implement proper error handling** with recovery strategies
4. **Monitor performance metrics** continuously
5. **Test strategies thoroughly** with backtesting before live trading
6. **Use version control** for strategy configurations
7. **Document your strategies** and their parameters

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're running from the correct directory
2. **Configuration Errors**: Use the validator to check your configs
3. **Data Issues**: Ensure market data files exist and are properly formatted
4. **Permission Errors**: Check file permissions for logs and data directories

### Getting Help

1. Check the main README.md for setup instructions
2. Review the test files for usage examples
3. Check the logs for detailed error information
4. Use the configuration validator to debug config issues

## Contributing

When adding new examples:

1. Follow the existing naming convention (`example_N_description`)
2. Include comprehensive docstrings
3. Add error handling
4. Include cleanup code for temporary files
5. Update this README with the new example

## License

This project is licensed under the MIT License - see the main LICENSE file for details.
