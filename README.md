# Hyperliquid Python Trading Bot

A comprehensive algorithmic trading system for the Hyperliquid DEX, featuring backtesting, live trading, and strategy development capabilities.

## Features

- **Backtesting Engine**: Test strategies against historical data with detailed performance metrics
- **Live Trading**: Execute trades on Hyperliquid DEX with real-time market data
- **Strategy Framework**: Modular strategy system with built-in indicators
- **Risk Management**: Position sizing, drawdown protection, and risk controls
- **Multiple Timeframes**: Support for 1m, 5m, 15m, 1h, 4h, 1d timeframes
- **Performance Analytics**: Comprehensive trade statistics and performance metrics

## Project Structure

```
hyperliquidpython/
├── src/                 # Source code
│   ├── application/     # Hyperliquid SDK integration
│   ├── backtesting/     # Backtesting engine and data
│   ├── cli/             # Command-line interfaces
│   ├── config/          # Configuration files
│   ├── core/            # Core trading components
│   ├── live/            # Live trading modules
│   ├── live_simulation/ # Paper trading simulation
│   ├── strategies/      # Trading strategies
│   └── utils/           # Utility functions
├── docs/                # Documentation
│   ├── guides/          # User guides and commands
│   ├── results/         # Performance results
│   └── deployment/      # Deployment guides
├── docker/              # Docker configuration
├── README.md            # This file
├── requirements.txt     # Python dependencies
└── setup.py            # Package setup
```

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd hyperliquidpython
```

2. Install dependencies:
```bash
# Option A: Automated setup (recommended)
./setup.sh

# Option B: Manual setup
pip install -r requirements.txt
cd src/application/hyperliquid_sdk
pip install -e .
cd ../../..
```

3. Set up configuration:
```bash
cp src/config/defaults.json src/config/your_config.json
# Edit your_config.json with your settings
```

### Running Backtests

Test a strategy against historical data:

```bash
cd src
source ../.venv/bin/activate
python -m cli.backtest --config config/core/backtest_eth.json
```

**📚 For complete command reference, see [STRATEGY_COMMANDS.md](STRATEGY_COMMANDS.md)**

### Live Trading

Start live trading (requires Hyperliquid API credentials):

```bash
python -m cli.trade --config config/live_eth.json
```

### Documentation

All documentation is organized in the `docs/` folder:

- **Guides** (`docs/guides/`) - User guides and command references
- **Results** (`docs/results/`) - Performance results and analysis  
- **Deployment** (`docs/deployment/`) - Setup and deployment guides

See `docs/README.md` for a complete overview.

### Strategy Development

Create custom strategies by extending the `BaseStrategy` class:

```python
from strategies.base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def should_open_position(self, data):
        # Your entry logic here
        return True
    
    def should_close_position(self, data, position):
        # Your exit logic here
        return True
```

## Available Strategies

- **BBRSI Strategy**: Bollinger Bands + RSI combination strategy
- **Scalping Strategy**: High-frequency scalping with tight stops
- **Debug Strategy**: Simple strategy for testing and debugging

## Configuration

Configuration files are located in `src/config/`:

- `defaults.json`: Default configuration values
- `backtest_*.json`: Backtesting configurations
- `live_*.json`: Live trading configurations

Key configuration options:
- `initial_capital`: Starting capital amount
- `max_position_size`: Maximum position size as fraction of capital
- `risk_per_trade`: Risk per trade as fraction of capital
- `commission`: Trading commission rate
- `slippage`: Expected slippage rate

## Performance Metrics

The system tracks comprehensive performance metrics:

- **Returns**: Total return, annualized return
- **Risk Metrics**: Sharpe ratio, maximum drawdown, volatility
- **Trade Statistics**: Win rate, profit factor, average trade duration
- **Risk-Adjusted Returns**: Sortino ratio, Calmar ratio

## Data Management

Historical data is stored in `src/backtesting/data/`:
- Supports multiple symbols (ETH-PERP, BTC-PERP, etc.)
- Multiple timeframes (1m, 5m, 15m, 1h, 4h, 1d)
- JSON format for easy processing

## Risk Management

Built-in risk management features:
- Position sizing based on volatility
- Maximum drawdown protection
- Stop-loss and take-profit levels
- Portfolio-level risk controls

## Development

### Adding New Indicators

Create indicator classes in `src/strategies/indicators/`:

```python
class MyIndicator:
    def __init__(self, period):
        self.period = period
    
    def calculate(self, data):
        # Your calculation logic
        return result
```

### Adding New Strategies

1. Create a new strategy file in `src/strategies/`
2. Extend the `BaseStrategy` class
3. Implement required methods
4. Add to strategy factory

### Testing

Run tests to verify functionality:

```bash
python -m pytest tests/
```

## API Integration

The system integrates with Hyperliquid DEX through the official SDK:
- Real-time market data via WebSocket
- Order placement and management
- Account information and balances
- Position tracking

## Logging

Comprehensive logging system:
- Trade execution logs
- Performance metrics
- Error tracking
- Debug information

Logs are stored in `src/logs/` with rotation and archival.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is for educational and research purposes only. Trading cryptocurrencies involves substantial risk of loss. Past performance does not guarantee future results. Use at your own risk.

## Support

For questions and support:
- Create an issue on GitHub
- Check the documentation in `docs/`
- Review example configurations in `src/config/`
**Ready to start trading?** Begin with backtesting to validate your strategy, then move to paper trading, and only consider live trading when you're confident in your approach.