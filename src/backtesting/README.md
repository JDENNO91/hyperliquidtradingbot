# 📊 Backtesting Module

This module provides historical backtesting for strategy validation and optimization.

## 📁 Structure

```
backtesting/
├── __init__.py
├── README.md                    # This file
├── improved_backtester.py       # Main backtesting engine
├── data/                        # Historical market data
│   ├── ETH-PERP/               # ETH perpetual data
│   └── BTC-PERP/               # BTC perpetual data
└── health/                     # Health check files
```

## 🚀 Usage

### Run Backtest
```bash
python -m cli.backtest --config config/core/backtest_eth.json
```

### Generate Data
```bash
cd src/backtesting/data/ETH-PERP/
python generate_eth_candles.py
```

### Health Check
```bash
python src/utils/health_check.py
```

## 🎯 Features

- **Historical Testing**: Test strategies against historical data
- **Performance Metrics**: Comprehensive statistics
- **Multiple Timeframes**: Support for 1m, 5m, 15m, 1h, 4h, 1d
- **Data Generation**: Synthetic data generation for testing
- **Strategy Validation**: Validate strategies before live trading

## 📊 Benefits

- **Fast Testing**: Quick strategy validation
- **Historical Analysis**: Learn from past market conditions
- **Optimization**: Fine-tune strategy parameters
- **Risk Assessment**: Understand strategy behavior