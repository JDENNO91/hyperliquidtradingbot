# 🚀 Trading Commands Reference

## 📊 **Quick Start Commands**

### **🕐 Timeframe Switching Commands**

#### **List Available Timeframes:**
```bash
python -m src.cli.timeframe_switcher --list-timeframes
```

#### **Compare Timeframes:**
```bash
python -m src.cli.timeframe_switcher --compare-timeframes
```

#### **List Strategies for Specific Timeframe:**
```bash
python -m src.cli.timeframe_switcher --list-strategies 15m
```

#### **Generate Custom Config:**
```bash
python -m src.cli.timeframe_switcher --generate-config 15m super_optimized_15m
```

---

## 🎯 **Strategy Testing Commands**

### **🥇 Champion Strategy (15m - 2.06% Return):**
```bash
python -m src.cli.backtest --config src/config/timeframe_optimized/backtest_super_optimized_15m_eth.json
```

### **🥈 Runner-Up Strategy (5m - 1.95% Return):**
```bash
python -m src.cli.backtest --config src/config/timeframe_optimized/backtest_super_optimized_5m_eth.json
```

### **🥉 Third Place Strategy (1m - 1.94% Return):**
```bash
python -m src.cli.backtest --config src/config/timeframe_optimized/backtest_super_optimized_eth.json
```

### **🔧 Core Strategies:**
```bash
# BBRSI Strategy (Original)
python -m src.cli.backtest --config src/config/core/backtest_eth.json

# Scalping Strategy (Original)
python -m src.cli.backtest --config src/config/core/backtest_scalping_eth.json
```


---

## 📈 **Data Generation Commands**

### **Generate Market Data:**
```bash
# Generate 10000 ETH candles
cd src/backtesting/data/ETH-PERP
python3 generate_eth_candles.py
cd <project-root>
```

### **Generate Different Data Sizes:**
```bash
# Edit generate_eth_candles.py to change num_candles
# Then run:
cd src/backtesting/data/ETH-PERP
python3 generate_eth_candles.py
cd <project-root>
```

---

## 🔧 **Development Commands**

### **Run Tests:**
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_strategies.py
```

### **Check Code Quality:**
```bash
# Lint code
python -m flake8 src/

# Type checking (if mypy is installed)
python -m mypy src/
```

---

## 🚀 **Live Trading Commands**

### **Live Simulation:**
```bash
# Run live simulation
python -m src.cli.simulate --config src/config/live_eth.json
```

### **Live Trading:**
```bash
# Run live trading (WARNING: Real money! Use --dry-run first)
python -m src.cli.trade --config src/config/live_eth.json --dry-run
```

---

## 📊 **Performance Monitoring Commands**

### **Monitor Performance:**
```bash
# Monitor live simulation performance
python src/live_simulation/monitor_performance.py

# Check trade statistics
python -c "from src.live_simulation.live_simulation_trade_statistics import LiveSimulationTradeStatistics; stats = LiveSimulationTradeStatistics(); print(stats.get_summary())"
```

### **View Logs:**
```bash
# View backtest logs
tail -f src/logs/backtest_trades.json

# View live simulation logs
tail -f src/logs/live_simulation_trades.json

# View error logs
tail -f src/logs/hyperliquid_trading_errors.log
```

---

## 🛠️ **Utility Commands**

### **Health Check:**
```bash
# Run health check
python -c "from src.utils.health_check import health_check; health_check()"
```

### **Check Credentials:**
```bash
# Verify Hyperliquid credentials
python tools/check_credentials.py
```

---

## 📁 **File Management Commands**

### **Clean Logs:**
```bash
# Clean old log files
rm -f src/logs/*.log
rm -f src/logs/*.json
```

---

## 🎯 **Quick Reference**

### **Best Performing Strategies:**
1. **Super Optimized 15m**: 2.06% return, 33.33% win rate
2. **Super Optimized 5m**: 1.95% return, 16.67% win rate
3. **Super Optimized 1m**: 1.94% return, 9.09% win rate

### **Recommended Commands for Daily Use:**
```bash
# Test champion strategy (15m - 2.06% return)
python -m src.cli.backtest --config src/config/timeframe_optimized/backtest_super_optimized_15m_eth.json

# Run live simulation
python -m src.cli.simulate --config src/config/live_eth.json

# Monitor performance
python src/live_simulation/monitor_performance.py
```

### **Emergency Commands:**
```bash
# Stop all processes
pkill -f "python.*trading"

# Clean everything
rm -f src/logs/*.log src/logs/*.json
```

---

## 📝 **Notes**

- Most commands can be run with `python -m src.cli.<command>` format
- Check logs regularly for errors (located in `src/logs/`)
- Test strategies thoroughly before live trading
- Monitor performance continuously during live trading
- For detailed strategy information, see [TRADING_STRATEGIES_GUIDE.md](TRADING_STRATEGIES_GUIDE.md)
