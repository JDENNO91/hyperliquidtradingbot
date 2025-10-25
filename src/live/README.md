# 💰 Live Trading Module

This module handles live trading with real money on Hyperliquid.

## 📁 Structure

```
live/
├── __init__.py
├── README.md                    # This file
├── run_live.py                  # Main live trading runner
├── live_risk_manager.py         # Risk management for live trading
├── live_trade_logger.py         # Trade logging for live trading
├── live_trade_statistics.py     # Statistics for live trading
├── utils.py                     # Live trading utilities
└── health/                      # Health check files
```

## 🚀 Usage

### Start Live Trading
```bash
python -m cli.trade --config config/live_eth.json
```

### Health Check
```bash
python src/utils/health_check.py
```

## ⚠️ Important Notes

- **Real Money**: This module trades with real money
- **Risk Management**: Always use proper risk management
- **Testing**: Test thoroughly with live simulation first
- **Monitoring**: Monitor trades closely when live

## 🔧 Configuration

Live trading requires:
- Valid Hyperliquid API credentials
- Proper risk management settings
- Tested strategy configuration
- Monitoring setup
