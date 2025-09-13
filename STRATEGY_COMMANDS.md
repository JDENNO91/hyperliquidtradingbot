# Strategy Commands Reference

This document provides comprehensive commands for running all available trading strategies in the Hyperliquid Python trading system.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Available Strategies](#available-strategies)
- [Backtesting Commands](#backtesting-commands)
- [Live Simulation Commands](#live-simulation-commands)
- [Live Trading Commands](#live-trading-commands)
- [Strategy Optimization Commands](#strategy-optimization-commands)
- [Configuration Files](#configuration-files)
- [Quick Start Examples](#quick-start-examples)

## Prerequisites

Before running any strategy commands, you need to set up the environment:

### 1. Install Dependencies

**Option A: Automated Setup (Recommended)**
```bash
# Run the setup script (one-time setup)
./setup.sh
```

**Option B: Manual Setup**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install the Hyperliquid SDK locally
cd src/application/hyperliquid_sdk
pip install -e .
cd ../../..
```

### 2. Activate Virtual Environment

```bash
# Activate the virtual environment
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows
```

### 3. Run Commands from src Directory

All strategy commands must be run from the `src` directory:

```bash
cd src
```

## Available Strategies

The system includes the following strategies:

### Core Strategies
- **BBRSI Strategy** (`bbrsi`) - Bollinger Bands + RSI combination strategy
- **Scalping Strategy** (`scalping`) - High-frequency scalping with tight stops

### Timeframe-Optimized Strategies (Champions)
- **Super Optimized Strategy** (`super_optimized`) - 1m timeframe, 1.94% return
- **Super Optimized 5m Strategy** (`super_optimized_5m`) - 5m timeframe, 1.95% return  
- **Super Optimized 15m Strategy** (`super_optimized_15m`) - 15m timeframe, 2.06% return (CHAMPION)

## Backtesting Commands

### Basic Backtesting

Run backtests using the improved backtester with smart data detection:

```bash
# BBRSI Strategy (ETH)
python -m cli.backtest --config config/core/backtest_eth.json

# Scalping Strategy (ETH)
python -m cli.backtest --config config/core/backtest_scalping_eth.json

# Super Optimized Strategy (ETH, 1m)
python -m cli.backtest --config config/timeframe_optimized/backtest_super_optimized_eth.json

# Super Optimized 5m Strategy (ETH)
python -m cli.backtest --config config/timeframe_optimized/backtest_super_optimized_5m_eth.json

# Super Optimized 15m Strategy (ETH) - CHAMPION
python -m cli.backtest --config config/timeframe_optimized/backtest_super_optimized_15m_eth.json

# BTC Backtesting
python -m cli.backtest --config config/backtest_btc.json
```

### Advanced Backtesting Options

```bash
# Specify custom data file
python -m cli.backtest --config config/core/backtest_eth.json --data src/backtesting/data/ETH-PERP/ETH-PERP-1m.json

# Save results to file
python -m cli.backtest --config config/core/backtest_eth.json --output results.json

# Verbose logging for debugging
python -m cli.backtest --config config/core/backtest_eth.json --log-level DEBUG

# Custom log file
python -m cli.backtest --config config/core/backtest_eth.json --log-file custom_backtest.log
```

### Risk Profile Backtesting

```bash
# High Risk ETH Strategy
python -m cli.backtest --config config/core/backtest_high_risk_eth.json

# Ultra High Risk ETH Strategy
python -m cli.backtest --config config/core/backtest_ultra_high_risk_eth.json

# Scalping High Risk ETH Strategy
python -m cli.backtest --config config/core/backtest_scalping_high_risk_eth.json

# Scalping Ultra Aggressive ETH Strategy
python -m cli.backtest --config config/core/backtest_scalping_ultra_aggressive_eth.json

# BBRSI Ultra Aggressive ETH Strategy
python -m cli.backtest --config config/core/backtest_bbrsi_ultra_aggressive_eth.json

# Balanced High Risk ETH Strategy
python -m cli.backtest --config config/core/backtest_balanced_high_risk_eth.json
```

## Live Simulation Commands

Live simulation allows you to test strategies with real market data without executing actual trades.

### Basic Live Simulation

```bash
# BBRSI Strategy Simulation (ETH)
python -m cli.simulate --profile live_eth

# Scalping Strategy Simulation
python -m cli.simulate --profile live_eth --strategy scalping

# Custom duration (4 hours)
python -m cli.simulate --profile live_eth --duration 4

# Custom market and timeframe
python -m cli.simulate --profile live_eth --market BTC-PERP --timeframe 15m
```

### Advanced Live Simulation Options

```bash
# Custom leverage and position size
python -m cli.simulate --profile live_eth --leverage 10 --position-size 0.1

# Custom capital amount
python -m cli.simulate --profile live_eth --capital 50000

# Maximum trades limit
python -m cli.simulate --profile live_eth --max-trades 50

# Verbose logging
python -m cli.simulate --profile live_eth --verbose

# Custom log file
python -m cli.simulate --profile live_eth --log-file simulation.log

# Save results to file
python -m cli.simulate --profile live_eth --output simulation_results.json
```

## Live Trading Commands

⚠️ **WARNING**: These commands execute real trades with real money. Use with extreme caution!

### Basic Live Trading

```bash
# BBRSI Strategy Live Trading (ETH)
python -m cli.trade --profile live_eth

# Dry run mode (no real trades)
python -m cli.trade --profile live_eth --dry-run

# Custom market and timeframe
python -m cli.trade --profile live_eth --market BTC-PERP --timeframe 15m
```

### Advanced Live Trading Options

```bash
# Custom trading parameters
python -m cli.trade --profile live_eth --leverage 5 --position-size 0.05 --capital 10000

# Risk management settings
python -m cli.trade --profile live_eth --max-risk-per-trade 0.02 --max-drawdown 0.1

# Trading duration and limits
python -m cli.trade --profile live_eth --duration 8h --max-trades 100

# Manual trade confirmation
python -m cli.trade --profile live_eth --confirm-trades

# Daily loss limit
python -m cli.trade --profile live_eth --max-daily-loss 0.05

# Custom start/end times
python -m cli.trade --profile live_eth --start-time "2024-01-01 09:00:00" --end-time "2024-01-01 17:00:00"

# Verbose logging
python -m cli.trade --profile live_eth --verbose

# Save results
python -m cli.trade --profile live_eth --output live_trading_results.json
```

## Strategy Optimization Commands

Optimize strategy parameters for better performance.

### Basic Optimization

```bash
# Optimize ETH strategy with default parameters
python -m cli.optimize --profile backtest_eth

# Optimize for specific metric
python -m cli.optimize --profile backtest_eth --metric sharpe_ratio

# Optimize BTC strategy
python -m cli.optimize --profile backtest_btc --metric profit_factor
```

### Advanced Optimization Options

```bash
# Custom parameter ranges
python -m cli.optimize --profile backtest_eth --rsi-periods 10,14,20 --bb-stddev 1.5,2.0,2.5

# Multiple parameter optimization
python -m cli.optimize --profile backtest_eth \
  --rsi-periods 10,14,20 \
  --rsi-overbought 65,70,75 \
  --rsi-oversold 25,30,35 \
  --bb-periods 15,20,25 \
  --bb-stddev 1.5,2.0,2.5 \
  --adx-periods 10,14,20 \
  --adx-thresholds 15,20,25

# Leverage and position size optimization
python -m cli.optimize --profile backtest_eth \
  --leverage-levels 3,5,10 \
  --position-sizes 0.05,0.1,0.2

# Parallel optimization
python -m cli.optimize --profile backtest_eth --parallel 4 --max-iterations 200

# Save optimization results
python -m cli.optimize --profile backtest_eth --output optimization_results.json

# Custom results directory
python -m cli.optimize --profile backtest_eth --results-dir my_optimization_results
```

## Configuration Files

### Core Strategy Configurations

| Strategy | Config File | Description |
|----------|-------------|-------------|
| BBRSI (ETH) | `config/core/backtest_eth.json` | Standard BBRSI strategy for ETH |
| Scalping (ETH) | `config/core/backtest_scalping_eth.json` | High-frequency scalping strategy |
| High Risk (ETH) | `config/core/backtest_high_risk_eth.json` | High-risk BBRSI variant |
| Ultra High Risk (ETH) | `config/core/backtest_ultra_high_risk_eth.json` | Ultra high-risk BBRSI variant |
| Scalping High Risk (ETH) | `config/core/backtest_scalping_high_risk_eth.json` | High-risk scalping variant |
| Scalping Ultra Aggressive (ETH) | `config/core/backtest_scalping_ultra_aggressive_eth.json` | Ultra aggressive scalping |
| BBRSI Ultra Aggressive (ETH) | `config/core/backtest_bbrsi_ultra_aggressive_eth.json` | Ultra aggressive BBRSI |
| Balanced High Risk (ETH) | `config/core/backtest_balanced_high_risk_eth.json` | Balanced high-risk approach |

### Timeframe-Optimized Configurations

| Strategy | Config File | Timeframe | Performance |
|----------|-------------|-----------|-------------|
| Super Optimized | `config/timeframe_optimized/backtest_super_optimized_eth.json` | 1m | 1.94% return |
| Super Optimized 5m | `config/timeframe_optimized/backtest_super_optimized_5m_eth.json` | 5m | 1.95% return |
| Super Optimized 15m | `config/timeframe_optimized/backtest_super_optimized_15m_eth.json` | 15m | 2.06% return (CHAMPION) |

### Live Trading Configurations

| Profile | Config File | Description |
|---------|-------------|-------------|
| Live ETH | `config/live_eth.json` | Live trading configuration for ETH |

## Quick Start Examples

### 1. Setup (First Time Only)

```bash
# Install dependencies
pip install -r requirements.txt

# Install Hyperliquid SDK
cd src/application/hyperliquid_sdk
pip install -e .
cd ../../..

# Activate virtual environment
source .venv/bin/activate

# Navigate to src directory
cd src
```

### 2. Test a Strategy with Backtesting

```bash
# Test the champion strategy (Super Optimized 15m)
python -m cli.backtest --config config/timeframe_optimized/backtest_super_optimized_15m_eth.json
```

### 3. Run Live Simulation

```bash
# Simulate BBRSI strategy for 4 hours
python -m cli.simulate --profile live_eth --strategy bbrsi --duration 4
```

### 4. Optimize Strategy Parameters

```bash
# Optimize BBRSI strategy for maximum Sharpe ratio
python -m cli.optimize --profile backtest_eth --metric sharpe_ratio --max-iterations 50
```

### 5. Live Trading (Use with Caution!)

```bash
# Start live trading with dry run first
python -m cli.trade --profile live_eth --dry-run

# If satisfied, run with real money (BE CAREFUL!)
python -m cli.trade --profile live_eth
```

## Command Line Options Reference

### Common Options

| Option | Description | Example |
|--------|-------------|---------|
| `--config`, `-c` | Configuration file path | `--config config/backtest_eth.json` |
| `--profile`, `-p` | Configuration profile name | `--profile live_eth` |
| `--market`, `-m` | Market to trade | `--market ETH-PERP` |
| `--timeframe`, `-t` | Trading timeframe | `--timeframe 15m` |
| `--leverage`, `-l` | Leverage multiplier | `--leverage 10` |
| `--position-size`, `-s` | Position size (0.0-1.0) | `--position-size 0.1` |
| `--capital`, `-c` | Initial capital | `--capital 10000` |
| `--verbose`, `-v` | Enable verbose logging | `--verbose` |
| `--log-file` | Custom log file | `--log-file custom.log` |
| `--output`, `-o` | Output file for results | `--output results.json` |

### Backtesting Specific Options

| Option | Description | Example |
|--------|-------------|---------|
| `--data`, `-d` | Market data file path | `--data data/ETH-PERP-1m.json` |
| `--log-level` | Logging level | `--log-level DEBUG` |

### Live Trading Specific Options

| Option | Description | Example |
|--------|-------------|---------|
| `--dry-run` | Run without executing real trades | `--dry-run` |
| `--confirm-trades` | Require manual confirmation | `--confirm-trades` |
| `--max-daily-loss` | Maximum daily loss limit | `--max-daily-loss 0.05` |
| `--max-risk-per-trade` | Maximum risk per trade | `--max-risk-per-trade 0.02` |
| `--max-drawdown` | Maximum allowed drawdown | `--max-drawdown 0.1` |
| `--duration` | Trading duration | `--duration 8h` |
| `--max-trades` | Maximum number of trades | `--max-trades 100` |

### Optimization Specific Options

| Option | Description | Example |
|--------|-------------|---------|
| `--metric`, `-m` | Optimization metric | `--metric sharpe_ratio` |
| `--max-iterations` | Maximum optimization iterations | `--max-iterations 100` |
| `--parallel` | Parallel processes | `--parallel 4` |
| `--rsi-periods` | RSI periods to test | `--rsi-periods 10,14,20` |
| `--bb-stddev` | Bollinger Band std devs | `--bb-stddev 1.5,2.0,2.5` |
| `--results-dir` | Results directory | `--results-dir my_results` |

## Notes

- Always test strategies with backtesting before live trading
- Use live simulation to validate strategies with real market data
- Start with small position sizes and low leverage when live trading
- Monitor your trades and adjust parameters as needed
- Keep detailed logs of all trading activities
- The Super Optimized 15m strategy is the current champion with 2.06% return

## Support

For more detailed information about each strategy and configuration options, refer to:
- `docs/guides/TRADING_STRATEGIES_GUIDE.md` - Strategy documentation
- `docs/guides/TRADING_COMMANDS.md` - Command reference
- `docs/guides/STRATEGY_SWITCHING_GUIDE.md` - Strategy switching guide
