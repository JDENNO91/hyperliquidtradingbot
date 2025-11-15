# Hyperliquid Trading Bot

A comprehensive Python trading bot for Hyperliquid DEX with multiple profitable strategies, backtesting, live simulation, and live trading capabilities.

## 🚀 Quick Start

### Installation
```bash
# Clone the repository
git clone https://github.com/JDENNO91/hyperliquidtradingbot.git
cd hyperliquidtradingbot

# Run the automated setup
./docs/setup-scripts/setup.sh
```

### First Backtest
```bash
# Run a quick backtest
python tests/test_core.py
```

## 📊 Project Structure

```
hyperliquidtradingbot/
├── src/                    # Core trading system
│   ├── strategies/         # Trading strategies
│   ├── backtesting/        # Backtesting engine
│   ├── live/              # Live trading
│   └── live_simulation/  # Paper trading
├── config/                # Configuration files
├── tests/                 # Test suite
└── docs/                  # Documentation
```

## 🎯 Strategies Explained

### 1. RSI Scalping Strategy
- **Timeframe**: 1m, 5m
- **Returns**: 97%+ in backtests
- **Risk**: High frequency, high reward
- **Best for**: Aggressive traders

### 2. MA+RSI Hybrid Strategy  
- **Timeframe**: 5m, 15m
- **Returns**: 85%+ in backtests
- **Risk**: Balanced approach
- **Best for**: Conservative traders

### 3. BBRSI Strategy
- **Timeframe**: 5m, 15m
- **Returns**: 90%+ in backtests
- **Risk**: Medium-high
- **Best for**: Technical traders

### 4. Super Optimized Strategy
- **Timeframe**: 5m, 15m
- **Returns**: 95%+ in backtests
- **Risk**: Optimized for performance
- **Best for**: Advanced traders

## 💻 Usage

### Backtesting
```bash
# Run backtest with specific strategy
python src/cli/backtest.py --strategy rsi_scalping --config config/core/backtest_eth.json

# Run optimization
python src/cli/optimize.py --strategy ma_rsi_hybrid
```

### Live Simulation
```bash
# Paper trading with real market data
python src/cli/simulate.py --strategy rsi_scalping --config config/production/rsi_scalping/standard_5m.json
```

### Live Trading
```bash
# Real trading (requires credentials)
python src/live/run_live.py --strategy rsi_scalping --config config/production/rsi_scalping/standard_5m.json
```

## ⚙️ Configuration

### Production Configs
- `config/production/rsi_scalping/` - RSI scalping configurations
- `config/production/ma_rsi_hybrid/` - MA+RSI hybrid configurations

### Strategy Switching
```bash
# Switch between strategies
python src/cli/strategy_switcher.py --strategy rsi_scalping
```

### Timeframe Switching
```bash
# Switch timeframes
python src/cli/timeframe_switcher.py --timeframe 5m
```

## 🔐 Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the template
cp config/env.template .env

# Edit with your credentials
nano .env
```

Required variables:
- `HL_API_URL` - Hyperliquid API endpoint
- `HL_PRIVATE_KEY` - Your private key
- `HL_ADDRESS` - Your wallet address

**Important Notes:**
- **Live Trading**: Requires real credentials
- **Live Simulation**: Uses testnet (no real money)
- **Backtesting**: No credentials needed

### Verify Credentials
```bash
python tools/check_credentials.py
```

## 📚 Documentation

- [Credential Setup Guide](docs/CREDENTIAL_SETUP.md)
- [Trading Strategies Guide](docs/guides/TRADING_STRATEGIES_GUIDE.md)
- [Strategy Switching Guide](docs/guides/STRATEGY_SWITCHING_GUIDE.md)
- [Trading Commands](docs/guides/TRADING_COMMANDS.md)
- [Production Strategies](docs/user-guides/PRODUCTION_STRATEGIES.md)

## 🧪 Testing

### Quick Health Check
```bash
python -c "from src.utils.health_check import health_check; print('✅ System healthy!' if health_check() else '❌ Issues found')"
```

### Core Test Suite
```bash
python tests/test_core.py
```

### Comprehensive Test Suite
```bash
python tests/test_project.py
```

### Individual Test Categories
```bash
# Integration tests
python -m pytest tests/test_integration.py -v

# Performance tests  
python -m pytest tests/test_performance.py -v

# Risk management tests
python -m pytest tests/test_risk_management.py -v

# Strategy tests
python -m pytest tests/test_strategies.py -v
```

**Test Coverage:**
- ✅ Integration tests (10/10 passing)
- ✅ Performance tests (3/3 passing)
- ✅ Risk management tests (4/4 passing)
- ✅ Strategy tests (5/5 passing)
- ✅ CLI tests (8/8 passing)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python tests/test_project.py`
5. Submit a pull request

## ⚠️ Risk Warning

**This software is for educational purposes only. Trading cryptocurrencies involves substantial risk of loss. Never trade with money you cannot afford to lose. Always test strategies thoroughly in simulation before live trading.**

## 📈 Performance Notes

- **Backtesting**: Historical data simulation
- **Live Simulation**: Real-time paper trading
- **Live Trading**: Real money trading
- **Risk Management**: Built-in position sizing and stop-losses

## 🔗 Links

- [Hyperliquid DEX](https://hyperliquid.xyz)
- [Hyperliquid SDK](src/application/hyperliquid_sdk/)
- [Full Credential Guide](docs/CREDENTIAL_SETUP.md)

---

**Built with ❤️ for the Hyperliquid community**