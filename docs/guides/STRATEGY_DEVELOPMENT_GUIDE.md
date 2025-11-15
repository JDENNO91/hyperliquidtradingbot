# Strategy Development Guide

This guide explains how to create and integrate new trading strategies into the Hyperliquid Trading Bot.

## Overview

Strategies are the core decision-making components of the trading system. They analyze market data and generate trading signals (LONG, SHORT, CLOSE) based on technical indicators and market conditions.

## Strategy Interface

All strategies must inherit from `BaseStrategy` and implement the required abstract methods:

```python
from src.core.base_strategy import BaseStrategy, Signal
from typing import Dict, Any, List

class MyStrategy(BaseStrategy):
    def compute_indicators(self, data: List[Dict[str, Any]], index: int) -> Dict[str, Any]:
        """Compute technical indicators for the current data point."""
        pass
    
    def generate_signal(self, data: List[Dict[str, Any]], index: int) -> Signal:
        """Generate a trading signal based on indicators and market conditions."""
        pass
```

## Step-by-Step: Creating a New Strategy

### Step 1: Create Strategy File

Create a new file in `src/strategies/core/` or `src/strategies/timeframe_optimized/`:

```python
# src/strategies/core/my_strategy.py

import logging
from typing import Dict, Any, List, Optional
from src.core.base_strategy import BaseStrategy, Signal
from src.strategies.indicators.rsi import calculate_rsi
from src.strategies.indicators.bollinger_bands import calculate_bollinger_bands

class MyStrategy(BaseStrategy):
    """
    My Custom Trading Strategy
    
    Description of what this strategy does and when it works best.
    """
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        super().__init__(config, logger)
        
        # Extract strategy-specific parameters
        indicators_config = config.get('indicators', {})
        self.rsi_period = indicators_config.get('rsi_period', 14)
        self.rsi_overbought = indicators_config.get('rsi_overbought', 70)
        self.rsi_oversold = indicators_config.get('rsi_oversold', 30)
        self.bb_period = indicators_config.get('bb_period', 20)
        self.bb_stddev = indicators_config.get('bb_stddev', 2.0)
        
        self.logger.info(f"MyStrategy initialized with RSI period={self.rsi_period}")
    
    def compute_indicators(self, data: List[Dict[str, Any]], index: int) -> Dict[str, Any]:
        """
        Compute all technical indicators needed for signal generation.
        
        Args:
            data: Historical market data (OHLCV candles)
            index: Current data point index
            
        Returns:
            Dictionary containing computed indicators
        """
        if index < max(self.rsi_period, self.bb_period):
            return {}
        
        # Extract price data
        closes = [candle['close'] for candle in data[index - self.rsi_period:index + 1]]
        highs = [candle['high'] for candle in data[index - self.bb_period:index + 1]]
        lows = [candle['low'] for candle in data[index - self.bb_period:index + 1]]
        
        # Calculate indicators using utility functions
        rsi = calculate_rsi(closes, period=self.rsi_period)
        bb = calculate_bollinger_bands(closes, period=self.bb_period, stddev=self.bb_stddev)
        
        current_price = data[index]['close']
        
        return {
            'rsi': rsi,
            'bb_upper': bb['upper'],
            'bb_middle': bb['middle'],
            'bb_lower': bb['lower'],
            'price': current_price,
            'bb_position': (current_price - bb['lower']) / (bb['upper'] - bb['lower']) if bb['upper'] != bb['lower'] else 0.5
        }
    
    def generate_signal(self, data: List[Dict[str, Any]], index: int) -> Signal:
        """
        Generate trading signal based on computed indicators.
        
        Args:
            data: Historical market data
            index: Current data point index
            
        Returns:
            Signal object with direction, strength, and reason
        """
        # Compute indicators
        indicators = self.compute_indicators(data, index)
        
        if not indicators:
            return Signal('NONE', 0.0, 'Insufficient data', {}, 0.0, '', 0.0)
        
        current_price = data[index]['close']
        symbol = self.market
        
        # Signal generation logic
        rsi = indicators['rsi']
        bb_position = indicators['bb_position']
        
        # LONG signal: RSI oversold + price near lower Bollinger Band
        if rsi < self.rsi_oversold and bb_position < 0.2:
            strength = min(1.0, (self.rsi_oversold - rsi) / 10.0)
            stop_loss = current_price * 0.98  # 2% stop loss
            return Signal(
                direction='LONG',
                strength=strength,
                reason=f'RSI oversold ({rsi:.2f}) + BB lower band',
                metadata={'rsi': rsi, 'bb_position': bb_position},
                price=current_price,
                symbol=symbol,
                timestamp=data[index].get('timestamp', 0),
                stop_loss=stop_loss
            )
        
        # SHORT signal: RSI overbought + price near upper Bollinger Band
        elif rsi > self.rsi_overbought and bb_position > 0.8:
            strength = min(1.0, (rsi - self.rsi_overbought) / 10.0)
            stop_loss = current_price * 1.02  # 2% stop loss
            return Signal(
                direction='SHORT',
                strength=strength,
                reason=f'RSI overbought ({rsi:.2f}) + BB upper band',
                metadata={'rsi': rsi, 'bb_position': bb_position},
                price=current_price,
                symbol=symbol,
                timestamp=data[index].get('timestamp', 0),
                stop_loss=stop_loss
            )
        
        # No signal
        return Signal('NONE', 0.0, 'No signal conditions met', {}, current_price, symbol, 0.0)
```

### Step 2: Register Strategy

Add your strategy to `src/strategies/strategy_factory.py`:

```python
from src.strategies.core.my_strategy import MyStrategy

class StrategyFactory:
    _strategies = {
        'bbrsi': BBRSIStrategy,
        'scalping': ScalpingStrategy,
        'my_strategy': MyStrategy,  # Add your strategy here
        # ... other strategies
    }
```

### Step 3: Create Configuration File

Create a config file in `src/config/production/my_strategy/`:

```json
{
  "trading": {
    "market": "ETH-PERP",
    "timeframe": "5m",
    "leverage": 10,
    "positionSize": 0.1,
    "positionSizePct": 0.1
  },
  "indicators": {
    "rsi_period": 14,
    "rsi_overbought": 70,
    "rsi_oversold": 30,
    "bb_period": 20,
    "bb_stddev": 2.0
  },
  "risk_management": {
    "max_risk_per_trade": 0.02,
    "max_drawdown": 0.15,
    "stop_loss_pct": 0.02,
    "take_profit_pct": 0.03,
    "trailing_stop_pct": 0.01
  },
  "strategy": {
    "name": "my_strategy",
    "type": "my_strategy"
  }
}
```

### Step 4: Test Your Strategy

#### Backtesting
```bash
python src/cli/backtest.py --config src/config/production/my_strategy/config.json --data src/backtesting/data/ETH-PERP/ETH-PERP-5m.json
```

#### Live Simulation
```bash
python src/cli/simulate.py --profile my_strategy
```

## Best Practices

### 1. Use Indicator Utilities

Always use indicator utility functions from `src/strategies/indicators/` rather than implementing your own:

```python
# ✅ Good
from src.strategies.indicators.rsi import calculate_rsi
rsi = calculate_rsi(closes, period=14)

# ❌ Bad
# Don't reimplement RSI calculation
```

### 2. Handle Edge Cases

Always check for sufficient data before computing indicators:

```python
def compute_indicators(self, data: List[Dict[str, Any]], index: int) -> Dict[str, Any]:
    min_required = max(self.rsi_period, self.bb_period)
    if index < min_required:
        return {}  # Return empty dict if insufficient data
    # ... compute indicators
```

### 3. Provide Clear Signal Reasons

Always provide descriptive reasons for signals:

```python
# ✅ Good
reason = f'RSI oversold ({rsi:.2f}) + price below BB lower band'

# ❌ Bad
reason = 'Signal'
```

### 4. Set Appropriate Stop Losses

Always set stop loss prices in signals:

```python
stop_loss = current_price * (1 - stop_loss_pct)  # For LONG
stop_loss = current_price * (1 + stop_loss_pct)  # For SHORT
```

### 5. Use Configurable Parameters

Make all strategy parameters configurable via config file:

```python
def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
    super().__init__(config, logger)
    indicators_config = config.get('indicators', {})
    self.my_parameter = indicators_config.get('my_parameter', default_value)
```

## Advanced: Position Management

Override `evaluate_position()` for custom exit logic:

```python
def evaluate_position(self, data: List[Dict[str, Any]], index: int) -> Signal:
    """
    Custom position evaluation logic.
    """
    if not self.current_position:
        return Signal('NONE', 0.0, 'No position', {}, 0.0, '', 0.0)
    
    current_price = data[index]['close']
    entry_price = self.current_position.entry_price
    
    # Custom exit logic
    if self.current_position.side == 'LONG':
        profit_pct = (current_price - entry_price) / entry_price
        
        # Trailing stop logic
        if profit_pct > 0.02:  # 2% profit
            trailing_stop = current_price * 0.99  # 1% trailing stop
            if current_price < trailing_stop:
                return Signal('CLOSE_LONG', 1.0, 'Trailing stop triggered', {}, current_price, '', 0.0)
    
    # Use default exit logic for other cases
    return super().evaluate_position(data, index)
```

## Testing Your Strategy

### Unit Tests

Create tests in `tests/test_strategies.py`:

```python
def test_my_strategy():
    config = {
        'trading': {'market': 'ETH-PERP', 'timeframe': '5m'},
        'indicators': {'rsi_period': 14}
    }
    strategy = MyStrategy(config)
    
    # Test indicator computation
    indicators = strategy.compute_indicators(test_data, len(test_data) - 1)
    assert 'rsi' in indicators
    
    # Test signal generation
    signal = strategy.generate_signal(test_data, len(test_data) - 1)
    assert signal.direction in ['LONG', 'SHORT', 'NONE']
```

### Backtesting Validation

Always validate your strategy with historical data:

```bash
# Run comprehensive backtest
python src/cli/backtest.py \
    --config src/config/production/my_strategy/config.json \
    --data src/backtesting/data/ETH-PERP/ETH-PERP-5m.json \
    --output results.json
```

Check the results for:
- Win rate > 50%
- Profit factor > 1.5
- Maximum drawdown < 20%
- Sharpe ratio > 1.0

## Common Patterns

### Mean Reversion Strategy
```python
# Buy when price deviates significantly below mean
if price < mean - 2 * stddev and rsi < 30:
    return Signal('LONG', ...)
```

### Trend Following Strategy
```python
# Buy when price breaks above moving average with momentum
if price > ma_20 and rsi > 50 and adx > 25:
    return Signal('LONG', ...)
```

### Breakout Strategy
```python
# Buy when price breaks above resistance with volume
if price > resistance_level and volume > avg_volume * 1.5:
    return Signal('LONG', ...)
```

## Troubleshooting

### Strategy Not Generating Signals
- Check indicator computation returns valid values
- Verify signal conditions are realistic
- Ensure sufficient historical data

### Strategy Generating Too Many Signals
- Increase signal strength thresholds
- Add additional filters (volume, volatility)
- Implement signal cooldown period

### Poor Backtest Performance
- Review signal logic
- Check for overfitting
- Test on different market conditions
- Consider walk-forward optimization

## Next Steps

1. **Optimize Parameters**: Use `src/cli/optimize.py` to find optimal parameters
2. **Walk-Forward Testing**: Test on out-of-sample data
3. **Live Simulation**: Validate with real market data
4. **Production Deployment**: Deploy to live trading after thorough testing

## Resources

- [Base Strategy Documentation](../core/base_strategy.py)
- [Indicator Utilities](../strategies/indicators/)
- [Configuration Guide](../config/)
- [Backtesting Guide](./BACKTESTING_GUIDE.md)


