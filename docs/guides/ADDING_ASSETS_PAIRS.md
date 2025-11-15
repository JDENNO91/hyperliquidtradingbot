# Adding New Assets/Pairs Guide

This guide explains how to add support for new trading pairs/assets to the Hyperliquid Trading Bot.

## Overview

Adding a new asset/pair involves:
1. Preparing market data for backtesting
2. Creating configuration files
3. Testing with backtesting engine
4. Validating with live simulation

## Step-by-Step Process

### Step 1: Prepare Market Data

#### Option A: Use Existing Data Generator

The project includes a market data generator for creating synthetic data:

```bash
cd src/backtesting/data
python generate_market_data.py
```

This will generate data for supported symbols. To add a new symbol, edit `generate_market_data.py`:

```python
# Add your symbol to the list
symbols = ['SOL-PERP', 'AVAX-PERP', 'MATIC-PERP', 'YOUR-SYMBOL-PERP']

# Add base price
base_prices = {
    'SOL-PERP': 50,
    'AVAX-PERP': 25,
    'MATIC-PERP': 0.8,
    'YOUR-SYMBOL-PERP': 100.0  # Add your base price
}

# Add volatility settings
volatility_settings = {
    'YOUR-SYMBOL-PERP': {'volatility': 0.025, 'trend': 0.0008}
}
```

#### Option B: Use Real Historical Data

1. **Obtain Historical Data**
   - Download OHLCV data from Hyperliquid API or data providers
   - Format: JSON array of candles

2. **Data Format**
   ```json
   [
     {
       "timestamp": 1640995200000,
       "open": 45000.0,
       "high": 45500.0,
       "low": 44800.0,
       "close": 45200.0,
       "volume": 1234.56
     },
     ...
   ]
   ```

3. **Create Data Directory**
   ```bash
   mkdir -p src/backtesting/data/YOUR-SYMBOL-PERP
   ```

4. **Save Data File**
   ```bash
   # Save as YOUR-SYMBOL-PERP-5m.json (or appropriate timeframe)
   cp your_data.json src/backtesting/data/YOUR-SYMBOL-PERP/YOUR-SYMBOL-PERP-5m.json
   ```

### Step 2: Create Configuration Files

#### Backtest Configuration

Create `src/config/backtest_your_symbol.json`:

```json
{
  "trading": {
    "market": "YOUR-SYMBOL-PERP",
    "timeframe": "5m",
    "leverage": 10,
    "positionSize": 0.1,
    "positionSizePct": 0.1,
    "initial_capital": 10000.0
  },
  "indicators": {
    "rsi_period": 14,
    "bb_period": 20,
    "bb_stddev": 2.0,
    "adx_period": 14
  },
  "risk_management": {
    "max_risk_per_trade": 0.02,
    "max_drawdown": 0.15,
    "stop_loss_pct": 0.015,
    "take_profit_pct": 0.03,
    "max_concurrent_positions": 1
  },
  "strategy": {
    "name": "bbrsi",
    "type": "bbrsi"
  },
  "data": {
    "path": "src/backtesting/data/YOUR-SYMBOL-PERP/YOUR-SYMBOL-PERP-5m.json"
  },
  "backtesting": {
    "slippage": 0.001,
    "fee_rate": 0.0005,
    "execution_latency_ms": 100
  }
}
```

#### Production Configuration

Create `src/config/production/your_strategy/your_symbol_5m.json`:

```json
{
  "trading": {
    "market": "YOUR-SYMBOL-PERP",
    "timeframe": "5m",
    "leverage": 10,
    "positionSize": 0.1,
    "positionSizePct": 0.1
  },
  "indicators": {
    "rsi_period": 14,
    "bb_period": 20,
    "bb_stddev": 2.0
  },
  "risk_management": {
    "max_risk_per_trade": 0.02,
    "max_drawdown": 0.15,
    "stop_loss_pct": 0.015,
    "take_profit_pct": 0.03,
    "trailing_stop_pct": 0.01
  },
  "strategy": {
    "name": "bbrsi",
    "type": "bbrsi"
  }
}
```

### Step 3: Verify Symbol on Hyperliquid

Check that your symbol is available on Hyperliquid:

```python
from src.application.hyperliquid_sdk.hyperliquid.info import Info

info = Info()
all_markets = info.meta()
print([coin['name'] for coin in all_markets['universe']])
```

Ensure your symbol exists in the list. Symbol format is typically `SYMBOL-PERP` for perpetuals.

### Step 4: Test with Backtesting

Run a backtest to validate your setup:

```bash
python src/cli/backtest.py \
    --config src/config/backtest_your_symbol.json \
    --data src/backtesting/data/YOUR-SYMBOL-PERP/YOUR-SYMBOL-PERP-5m.json
```

**Check Results:**
- ✅ No errors during execution
- ✅ Trades are executed
- ✅ Performance metrics are calculated
- ✅ Results are saved correctly

### Step 5: Validate with Live Simulation

Test with real market data (no real money):

```bash
python src/cli/simulate.py \
    --profile your_symbol_5m \
    --duration 1
```

**Monitor:**
- Market data is received correctly
- Signals are generated
- Orders would be executed (simulated)
- No errors or warnings

### Step 6: Adjust Strategy Parameters

Different assets may require different parameters:

#### High Volatility Assets
- Increase stop loss percentage
- Reduce position size
- Use longer timeframes

#### Low Volatility Assets
- Reduce stop loss percentage
- Increase position size
- Use shorter timeframes

#### Example Adjustments

```json
{
  "risk_management": {
    "stop_loss_pct": 0.02,      // Higher for volatile assets
    "take_profit_pct": 0.04,    // Higher target for volatile assets
    "max_risk_per_trade": 0.015 // Lower risk for volatile assets
  },
  "indicators": {
    "bb_stddev": 2.5  // Wider bands for volatile assets
  }
}
```

## Asset-Specific Considerations

### Perpetual Contracts (PERP)
- Standard format: `SYMBOL-PERP`
- No expiration date
- Funding fees apply
- High leverage available

### Spot Markets
- Format: `SYMBOL` (no -PERP suffix)
- Lower leverage typically
- No funding fees
- Different risk profile

### Cross-Margin vs Isolated Margin
- **Cross-Margin**: All positions share margin
- **Isolated Margin**: Each position has separate margin
- Configure in trading settings

## Data Requirements

### Minimum Data Requirements
- **Backtesting**: At least 1000 candles (preferably 5000+)
- **Timeframes**: 1m, 5m, 15m, 1h data recommended
- **Data Quality**: Clean, no gaps, accurate OHLCV

### Data Validation

Create a validation script:

```python
import json
from pathlib import Path

def validate_market_data(file_path: str):
    """Validate market data file format and quality."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Check format
    assert isinstance(data, list), "Data must be a list"
    assert len(data) > 0, "Data cannot be empty"
    
    # Check required fields
    required_fields = ['open', 'high', 'low', 'close', 'volume']
    for i, candle in enumerate(data):
        for field in required_fields:
            assert field in candle, f"Missing field '{field}' in candle {i}"
            assert isinstance(candle[field], (int, float)), f"Invalid type for '{field}' in candle {i}"
        
        # Validate OHLC logic
        assert candle['high'] >= candle['low'], f"Invalid OHLC in candle {i}"
        assert candle['high'] >= candle['open'], f"Invalid OHLC in candle {i}"
        assert candle['high'] >= candle['close'], f"Invalid OHLC in candle {i}"
        assert candle['low'] <= candle['open'], f"Invalid OHLC in candle {i}"
        assert candle['low'] <= candle['close'], f"Invalid OHLC in candle {i}"
    
    print(f"✅ Validated {len(data)} candles")
    return True

# Usage
validate_market_data("src/backtesting/data/YOUR-SYMBOL-PERP/YOUR-SYMBOL-PERP-5m.json")
```

## Troubleshooting

### Symbol Not Found
- **Issue**: Symbol doesn't exist on Hyperliquid
- **Solution**: Check symbol name, ensure it's a valid perpetual contract

### No Market Data
- **Issue**: Cannot fetch market data
- **Solution**: Verify API connection, check symbol availability

### Poor Backtest Results
- **Issue**: Strategy doesn't work well for this asset
- **Solution**: Adjust parameters, try different timeframes, test different strategies

### Configuration Errors
- **Issue**: Config validation fails
- **Solution**: Check JSON syntax, verify all required fields are present

## Best Practices

### 1. Start with Backtesting
Always test thoroughly with historical data before live trading.

### 2. Use Multiple Timeframes
Test your asset on different timeframes (1m, 5m, 15m, 1h) to find optimal settings.

### 3. Validate Data Quality
Ensure your market data is clean and accurate before using it.

### 4. Monitor Live Simulation
Run live simulation for at least 24 hours before going live.

### 5. Start Small
When going live, start with small position sizes and gradually increase.

### 6. Document Parameters
Keep notes on what parameters work best for each asset.

## Example: Adding SOL-PERP

```bash
# 1. Create data directory
mkdir -p src/backtesting/data/SOL-PERP

# 2. Generate or download data
# (Use data generator or download from API)

# 3. Create config
cp src/config/backtest_eth.json src/config/backtest_sol.json
# Edit market: "SOL-PERP"

# 4. Test backtest
python src/cli/backtest.py --config src/config/backtest_sol.json

# 5. Create production config
mkdir -p src/config/production/rsi_scalping
cp src/config/production/rsi_scalping/standard_5m.json \
   src/config/production/rsi_scalping/sol_5m.json
# Edit market: "SOL-PERP"

# 6. Test simulation
python src/cli/simulate.py --profile sol_5m --duration 1
```

## Resources

- [Hyperliquid API Documentation](https://hyperliquid.gitbook.io/hyperliquid-docs)
- [Market Data Format](../backtesting/data/)
- [Configuration Guide](../config/)
- [Strategy Development Guide](./STRATEGY_DEVELOPMENT_GUIDE.md)


