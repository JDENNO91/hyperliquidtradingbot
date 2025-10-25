# 🎮 Live Simulation Module

This module provides paper trading simulation for testing strategies without real money.

## 📁 Structure

```
live_simulation/
├── __init__.py
├── README.md                           # This file
├── run_live_simulation.py              # Main simulation runner
├── live_simulation_trade_logger.py     # Trade logging for simulation
├── live_simulation_trade_statistics.py # Statistics for simulation
├── monitor_performance.py              # Performance monitoring
├── simple_risk_manager.py              # Risk management for simulation
├── utils.py                            # Simulation utilities
└── health/                             # Health check files
```

## 🚀 Usage

### Start Live Simulation
```bash
python -m cli.simulate --profile live_eth
```

### Monitor Performance
```bash
python src/live_simulation/monitor_performance.py
```

### Health Check
```bash
python src/utils/health_check.py
```

## 🎯 Features

- **Paper Trading**: Test strategies without real money
- **Real-time Data**: Uses live market data
- **Performance Monitoring**: Track strategy performance
- **Risk Management**: Simulated risk controls
- **Trade Logging**: Detailed trade history

## 📊 Benefits

- **Safe Testing**: No financial risk
- **Real Conditions**: Uses live market data
- **Performance Analysis**: Detailed statistics
- **Strategy Validation**: Test before going live