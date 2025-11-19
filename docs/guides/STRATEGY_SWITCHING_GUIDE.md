# Strategy Switching Guide

This guide shows how to switch between trading strategies. For detailed strategy information, see [TRADING_STRATEGIES_GUIDE.md](TRADING_STRATEGIES_GUIDE.md) or [../user-guides/PRODUCTION_STRATEGIES.md](../user-guides/PRODUCTION_STRATEGIES.md).

## Quick Strategy Switching

### Method 1: Using the Strategy Switcher CLI

```bash
# List all available strategies
python -m src.cli.strategy_switcher list

# Compare strategies
python -m src.cli.strategy_switcher compare

# Get strategy recommendation
python -m src.cli.strategy_switcher recommend volatile high

# Generate configuration for a strategy
python -m src.cli.strategy_switcher config bbrsi --mode backtest --output my_config.json

# Run backtest with specific strategy
python -m src.cli.strategy_switcher backtest scalping --capital 5000 --risk 0.01
```

### Method 2: Using Python Code

```python
from src.config.strategy_switcher import StrategySwitcher, switch_to_strategy

# Easy switching
bbrsi_config = switch_to_strategy('bbrsi', initial_capital=10000, risk_per_trade=0.02)
scalping_config = switch_to_strategy('scalping', initial_capital=5000, risk_per_trade=0.01)

# Advanced usage
switcher = StrategySwitcher()

# Get strategy recommendation
recommended = switcher.get_strategy_recommendation('volatile', 'high')
print(f"Recommended strategy: {recommended}")

# Create custom configuration
config = switcher.create_backtest_config('bbrsi', 
                                        symbol='BTC-PERP',
                                        initial_capital=20000,
                                        risk_per_trade=0.015)
```

### Method 3: Direct Configuration Files

```bash
# Use BBRSI strategy
python -m src.cli.backtest --config src/config/backtest_eth.json

# Use Scalping strategy  
python -m src.cli.backtest --config src/config/backtest_scalping_eth.json
```

## Strategy Selection

See [TRADING_STRATEGIES_GUIDE.md](TRADING_STRATEGIES_GUIDE.md) for detailed strategy selection guidance.

## Configuration Customization

Both strategies support extensive customization:

```python
# Custom BBRSI configuration
bbrsi_config = switch_to_strategy('bbrsi',
    initial_capital=15000,
    risk_per_trade=0.025,
    indicators={
        'rsi': {'period': 21, 'overbought': 75, 'oversold': 25},
        'bollinger': {'period': 25, 'stdDev': 2.5}
    }
)

# Custom Scalping configuration
scalping_config = switch_to_strategy('scalping',
    initial_capital=8000,
    risk_per_trade=0.008,
    trading={
        'entry_threshold': 0.0015,
        'exit_threshold': 0.004,
        'max_hold_time': 180
    }
)
```

For performance comparisons, see [../user-guides/PRODUCTION_STRATEGIES.md](../user-guides/PRODUCTION_STRATEGIES.md).

## Quick Start Examples

### Example 1: Conservative Trading
```bash
python -m src.cli.strategy_switcher backtest bbrsi --capital 10000 --risk 0.01
```

### Example 2: Aggressive Trading
```bash
python -m src.cli.strategy_switcher backtest scalping --capital 5000 --risk 0.02
```

### Example 3: Get Recommendation
```bash
python -m src.cli.strategy_switcher recommend trending medium
```

## Advanced Features

### Strategy Comparison
```python
switcher = StrategySwitcher()
comparison = switcher.compare_strategies(['bbrsi', 'scalping'])
print(comparison)
```

### Custom Strategy Registration
```python
# Register a new strategy (future feature)
switcher.register_strategy('my_strategy', MyCustomStrategy)
```

### Configuration Validation
```python
# Validate strategy configuration
is_valid, errors = switcher.validate_strategy_config('bbrsi', config)
```

## Tips for Strategy Selection

1. **Start with BBRSI** for beginners - it's more forgiving
2. **Use Scalping** when you have experience and can monitor positions closely
3. **Consider market conditions** - use the recommendation system
4. **Test both strategies** with backtesting before going live
5. **Customize parameters** based on your risk tolerance

## Troubleshooting

### Common Issues:
- **"Unknown strategy"**: Make sure you're using 'bbrsi' or 'scalping'
- **Configuration errors**: Check that all required parameters are provided
- **Import errors**: Ensure PYTHONPATH includes the src directory

### Getting Help:
```bash
python -m src.cli.strategy_switcher --help
python -m src.cli.strategy_switcher config --help
```

For more information on strategies, see [TRADING_STRATEGIES_GUIDE.md](TRADING_STRATEGIES_GUIDE.md) or [../user-guides/PRODUCTION_STRATEGIES.md](../user-guides/PRODUCTION_STRATEGIES.md).
