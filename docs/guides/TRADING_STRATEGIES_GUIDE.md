# 🚀 Trading Strategies Guide

This comprehensive guide explains the two main trading strategies, their functionality, and how to use them across different trading modes.

## 📊 Available Strategies

### 1. **BBRSI Strategy** - Mean Reversion with Trend Confirmation

**Strategy Type**: Mean reversion with trend confirmation  
**Risk Level**: Medium  
**Best For**: Trending and ranging markets  
**Hold Time**: Medium (minutes to hours)

#### **How It Works:**
- **RSI Analysis**: Uses multiple RSI thresholds (35/40/50) for oversold/overbought detection
- **Bollinger Bands**: Analyzes price position relative to bands for mean reversion signals
- **ADX Trend Filter**: Confirms trend strength to avoid counter-trend trades
- **Volatility Filter**: Only trades during sufficient market volatility
- **Multi-Factor Scoring**: Requires 3+ points from various indicators for entry

#### **Entry Conditions:**
- **LONG**: RSI oversold + price at lower Bollinger Band + upward momentum
- **SHORT**: RSI overbought + price at upper Bollinger Band + downward momentum

#### **Exit Conditions:**
- **Take Profit**: 0.5% profit target
- **Stop Loss**: 0.3% stop loss
- **Time Exit**: Maximum hold time reached

---

### 2. **Scalping Strategy** - High-Frequency Price Action

**Strategy Type**: High-frequency price action  
**Risk Level**: High  
**Best For**: Volatile markets with high liquidity  
**Hold Time**: Short (seconds to minutes)

#### **How It Works:**
- **Multi-Timeframe Momentum**: Analyzes 1m and 5m price momentum alignment
- **Price Acceleration**: Detects second derivative of price movement
- **Volume Confirmation**: Requires volume spikes for signal validation
- **Support/Resistance**: Uses recent highs/lows for entry positioning
- **ATR Volatility**: Ensures sufficient volatility for scalping opportunities

#### **Entry Conditions:**
- **LONG**: Strong upward momentum + volume spike + price acceleration + near support
- **SHORT**: Strong downward momentum + volume spike + price acceleration + near resistance

#### **Exit Conditions:**
- **Take Profit**: 0.5% profit target
- **Stop Loss**: 0.3% stop loss
- **Time Exit**: Maximum 5-minute hold time

---

## 🎯 Trading Modes

### **1. Backtesting Mode** - Historical Strategy Testing

**Purpose**: Test strategies against historical data to evaluate performance  
**Risk**: None (simulated trading)  
**Data**: Historical market data files  
**Best For**: Strategy development, optimization, and validation

#### **Commands:**

```bash
# Test BBRSI Strategy
python -m cli.backtest --config src/config/backtest_eth.json

# Test Scalping Strategy  
python -m cli.backtest --config src/config/backtest_scalping_eth.json

# Use improved backtester (recommended)
PYTHONPATH=src python3 src/cli/improved_backtest.py --config src/config/backtest_eth.json

# Save results to file
PYTHONPATH=src python3 src/cli/improved_backtest.py --config src/config/backtest_eth.json --output results.json

# Debug mode with detailed logging
PYTHONPATH=src python3 src/cli/improved_backtest.py --config src/config/backtest_eth.json --log-level DEBUG
```

#### **Configuration Files:**
- `src/config/backtest_eth.json` - BBRSI strategy configuration
- `src/config/backtest_scalping_eth.json` - Scalping strategy configuration

---

### **2. Live Simulation Mode** - Real-Time Paper Trading

**Purpose**: Test strategies with real-time market data without real money  
**Risk**: None (paper trading)  
**Data**: Live market data from Hyperliquid  
**Best For**: Strategy validation in live market conditions

#### **Commands:**

```bash
# Run BBRSI live simulation
PYTHONPATH=src python3 src/live_simulation/run_live_simulation.py --config src/config/live_eth.json --strategy bbrsi

# Run Scalping live simulation
PYTHONPATH=src python3 src/live_simulation/run_live_simulation.py --config src/config/live_eth.json --strategy scalping

# Monitor performance
PYTHONPATH=src python3 src/live_simulation/monitor_performance.py
```

#### **Configuration Files:**
- `src/config/live_eth.json` - Live trading configuration
- `src/config/live_simulation_eth.json` - Live simulation specific settings

---

### **3. Live Trading Mode** - Real Money Trading

**Purpose**: Execute real trades with actual capital  
**Risk**: HIGH (real money at risk)  
**Data**: Live market data from Hyperliquid  
**Best For**: Production trading with proven strategies

#### **Commands:**

```bash
# Run live trading (REAL MONEY - USE WITH CAUTION)
PYTHONPATH=src python3 src/live/run_live.py --config src/config/live_eth.json --strategy bbrsi

# Run with specific risk settings
PYTHONPATH=src python3 src/live/run_live.py --config src/config/live_eth.json --strategy scalping --max-position-size 0.02

# Monitor live performance
PYTHONPATH=src python3 src/live/monitor_performance.py
```

#### **⚠️ IMPORTANT WARNINGS:**
- **REAL MONEY AT RISK**: Live trading uses actual capital
- **Start Small**: Begin with minimal position sizes
- **Monitor Closely**: Watch performance continuously
- **Test First**: Always backtest and simulate before live trading

---

## 🔧 Strategy Configuration

### **BBRSI Strategy Settings:**

```json
{
  "strategy": "bbrsi",
  "indicators": {
    "rsi": {
      "period": 14,
      "overbought": 55,
      "oversold": 45
    },
    "bollinger": {
      "period": 20,
      "stdDev": 2
    },
    "adx": {
      "period": 14,
      "threshold": 3
    }
  },
  "trading": {
    "profit_target": 0.005,
    "stop_loss": 0.003,
    "max_hold_time": 1800
  }
}
```

### **Scalping Strategy Settings:**

```json
{
  "strategy": "scalping",
  "trading": {
    "entry_threshold": 0.002,
    "exit_threshold": 0.005,
    "max_hold_time": 300,
    "volume_multiplier": 1.5,
    "stop_loss_pct": 0.003
  }
}
```

---

## 📈 Performance Comparison

| Strategy | Win Rate | Avg Hold Time | Risk Level | Best Market Conditions |
|----------|----------|---------------|------------|----------------------|
| **BBRSI** | 4-8% | 15-30 minutes | Medium | Trending, ranging |
| **Scalping** | 2-5% | 2-5 minutes | High | Volatile, liquid |

---

## 🛠️ Strategy Switching

### **Easy Strategy Switching:**

```bash
# List available strategies
PYTHONPATH=src python3 src/cli/strategy_switcher.py list

# Compare strategies
PYTHONPATH=src python3 src/cli/strategy_switcher.py compare

# Get strategy recommendation
PYTHONPATH=src python3 src/cli/strategy_switcher.py recommend volatile high

# Generate new config for strategy
PYTHONPATH=src python3 src/cli/strategy_switcher.py generate scalping --output new_config.json
```

---

## 📊 Monitoring and Analysis

### **Performance Monitoring:**

```bash
# View backtest results
cat src/backtesting/unified_backtest_results.json

# Monitor live simulation
tail -f src/logs/live_simulation_trades.json

# Check live trading performance
tail -f src/logs/live_trades.json
```

### **Key Metrics to Watch:**
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Gross profit / Gross loss
- **Max Drawdown**: Largest peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted returns
- **Average Hold Time**: Time positions are held

---

## 🚨 Risk Management

### **Position Sizing:**
- **Conservative**: 1-2% of capital per trade
- **Moderate**: 2-5% of capital per trade
- **Aggressive**: 5-10% of capital per trade

### **Risk Controls:**
- **Stop Loss**: Always use stop losses
- **Position Limits**: Limit concurrent positions
- **Drawdown Limits**: Stop trading at max drawdown
- **Time Limits**: Maximum hold times

---

## 🔍 Troubleshooting

### **Common Issues:**

1. **No Trades Generated:**
   - Check market data availability
   - Verify strategy parameters
   - Ensure sufficient volatility

2. **High Loss Rate:**
   - Adjust entry thresholds
   - Tighten stop losses
   - Reduce position sizes

3. **Connection Issues:**
   - Check internet connection
   - Verify API credentials
   - Monitor system logs

### **Debug Commands:**

```bash
# Enable debug logging
--log-level DEBUG

# Check system health
PYTHONPATH=src python3 src/quick_health_check.py

# Test connections
PYTHONPATH=src python3 src/test_connections.py
```

---

## 📚 Additional Resources

- **Strategy Development**: `src/strategies/README.md`
- **Configuration Guide**: `src/config/README.md`
- **Live Trading Setup**: `src/live/README.md`
- **Backtesting Guide**: `src/backtesting/README.md`

---

## ⚠️ Disclaimer

**Trading involves substantial risk of loss and is not suitable for all investors. Past performance is not indicative of future results. Always test strategies thoroughly before using real money.**
