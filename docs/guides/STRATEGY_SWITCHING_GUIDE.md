# Strategy Switching Guide

This guide shows how to easily switch between the two improved trading strategies using the new strategy switching system.

## Available Strategies

### 1. BBRSI Strategy
- **Type**: Mean reversion with trend confirmation
- **Risk Level**: Medium
- **Best For**: Trending and ranging markets
- **Characteristics**: Balanced risk/reward, medium hold times

### 2. Scalping Strategy  
- **Type**: High-frequency price action
- **Risk Level**: High
- **Best For**: Volatile markets
- **Characteristics**: Tight risk/reward, short hold times

## Quick Strategy Switching

### Method 1: Using the Strategy Switcher CLI

```bash
# List all available strategies
python src/cli/strategy_switcher.py list

# Compare strategies
python src/cli/strategy_switcher.py compare

# Get strategy recommendation
python src/cli/strategy_switcher.py recommend volatile high

# Generate configuration for a strategy
python src/cli/strategy_switcher.py config bbrsi --mode backtest --output my_config.json

# Run backtest with specific strategy
python src/cli/strategy_switcher.py backtest scalping --capital 5000 --risk 0.01
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
python src/cli/backtest.py --config src/config/backtest_eth.json

# Use Scalping strategy  
python src/cli/backtest.py --config src/config/backtest_scalping_eth.json
```

## Strategy Selection Guide

### Choose BBRSI Strategy When:
- Market is trending or ranging
- You prefer medium risk/reward
- You want balanced entry frequency
- You're comfortable with medium hold times

### Choose Scalping Strategy When:
- Market is highly volatile
- You prefer high-frequency trading
- You want tight risk management
- You're comfortable with short hold times

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

## Performance Comparison

| Strategy | Risk Level | Entry Frequency | Hold Time | Best Market Conditions |
|----------|------------|-----------------|-----------|----------------------|
| BBRSI    | Medium     | Medium          | Medium    | Trending/Ranging     |
| Scalping | High       | High            | Short     | Volatile             |

## Quick Start Examples

### Example 1: Conservative Trading
```bash
python src/cli/strategy_switcher.py backtest bbrsi --capital 10000 --risk 0.01
```

### Example 2: Aggressive Trading
```bash
python src/cli/strategy_switcher.py backtest scalping --capital 5000 --risk 0.02
```

### Example 3: Get Recommendation
```bash
python src/cli/strategy_switcher.py recommend trending medium
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
python src/cli/strategy_switcher.py --help
python src/cli/strategy_switcher.py config --help
```

This system makes it incredibly easy to switch between strategies and experiment with different approaches to find what works best for your trading style and market conditions.
