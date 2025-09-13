# 🚀 Trading Commands Reference

## 📊 **Quick Start Commands**

### **🕐 Timeframe Switching Commands**

#### **List Available Timeframes:**
```bash
PYTHONPATH=src python3 src/cli/timeframe_switcher.py --list-timeframes
```

#### **Compare Timeframes:**
```bash
PYTHONPATH=src python3 src/cli/timeframe_switcher.py --compare-timeframes
```

#### **List Strategies for Specific Timeframe:**
```bash
PYTHONPATH=src python3 src/cli/timeframe_switcher.py --list-strategies 15m
```

#### **Generate Custom Config:**
```bash
PYTHONPATH=src python3 src/cli/timeframe_switcher.py --generate-config 15m super_optimized_15m
```

---

## 🎯 **Strategy Testing Commands**

### **🥇 Champion Strategy (15m - 2.06% Return):**
```bash
PYTHONPATH=src python3 src/cli/improved_backtest.py --config src/config/timeframe_optimized/backtest_super_optimized_15m_eth.json
```

### **🥈 Runner-Up Strategy (5m - 1.95% Return):**
```bash
PYTHONPATH=src python3 src/cli/improved_backtest.py --config src/config/timeframe_optimized/backtest_super_optimized_5m_eth.json
```

### **🥉 Third Place Strategy (1m - 1.94% Return):**
```bash
PYTHONPATH=src python3 src/cli/improved_backtest.py --config src/config/timeframe_optimized/backtest_super_optimized_eth.json
```

### **🔧 Core Strategies:**
```bash
# BBRSI Strategy (Original)
PYTHONPATH=src python3 src/cli/improved_backtest.py --config src/config/core/backtest_eth.json

# Scalping Strategy (Original)
PYTHONPATH=src python3 src/cli/improved_backtest.py --config src/config/core/backtest_scalping_eth.json
```


---

## 📈 **Data Generation Commands**

### **Generate Market Data:**
```bash
# Generate 10000 ETH candles
cd src/backtesting/data/ETH-PERP
python3 generate_eth_candles.py
cd /Users/jdennis/Documents/GitHub/hyperliquidpython
```

### **Generate Different Data Sizes:**
```bash
# Edit generate_eth_candles.py to change num_candles
# Then run:
cd src/backtesting/data/ETH-PERP
python3 generate_eth_candles.py
cd /Users/jdennis/Documents/GitHub/hyperliquidpython
```

---

## 🔧 **Development Commands**

### **Run Tests:**
```bash
# Run all tests
PYTHONPATH=src python3 -m pytest

# Run specific test
PYTHONPATH=src python3 -m pytest tests/test_strategies.py
```

### **Check Code Quality:**
```bash
# Lint code
PYTHONPATH=src python3 -m flake8 src/

# Type checking
PYTHONPATH=src python3 -m mypy src/
```

### **Generate Documentation:**
```bash
# Generate API docs
PYTHONPATH=src python3 -m pydoc -w src/strategies/

# Generate strategy docs
PYTHONPATH=src python3 -m pydoc -w src/strategies/super_optimized_15m_strategy.py
```

---

## 🚀 **Live Trading Commands**

### **Live Simulation:**
```bash
# Run live simulation with champion strategy
PYTHONPATH=src python3 src/live_simulation/run_live_simulation.py --config src/config/live_eth.json --strategy super_optimized_15m

# Run live simulation with 5m strategy
PYTHONPATH=src python3 src/live_simulation/run_live_simulation.py --config src/config/live_eth.json --strategy super_optimized_5m
```

### **Live Trading:**
```bash
# Run live trading (WARNING: Real money!)
PYTHONPATH=src python3 src/live/run_live.py --config src/config/live_eth.json --strategy super_optimized_15m
```

---

## 📊 **Performance Monitoring Commands**

### **Monitor Performance:**
```bash
# Monitor live simulation performance
PYTHONPATH=src python3 src/live_simulation/monitor_performance.py

# Check trade statistics
PYTHONPATH=src python3 src/live_simulation/live_simulation_trade_statistics.py
```

### **View Logs:**
```bash
# View backtest logs
tail -f logs/backtest_trades.json

# View live simulation logs
tail -f logs/live_simulation_trades.json

# View error logs
tail -f logs/__main___errors.log
```

---

## 🛠️ **Utility Commands**

### **Health Check:**
```bash
# Run health check
PYTHONPATH=src python3 src/quick_health_check.py
```

### **Test Connections:**
```bash
# Test Hyperliquid connection
PYTHONPATH=src python3 src/test_connections.py
```

### **Strategy Analysis:**
```bash
# Analyze strategy performance
PYTHONPATH=src python3 src/strategies/strategy_analysis.py
```

---

## 📁 **File Management Commands**

### **Clean Logs:**
```bash
# Clean old log files
rm -f logs/*.log
rm -f logs/*.json
```

### **Clean Database:**
```bash
# Clean database files
rm -f db/*.db
```

### **Backup Results:**
```bash
# Backup results
cp -r logs/ backup/logs_$(date +%Y%m%d_%H%M%S)/
cp -r db/ backup/db_$(date +%Y%m%d_%H%M%S)/
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
PYTHONPATH=src python3 src/cli/improved_backtest.py --config src/config/timeframe_optimized/backtest_super_optimized_15m_eth.json

# Run live simulation
PYTHONPATH=src python3 src/live_simulation/run_live_simulation.py --config src/config/live_eth.json --strategy super_optimized_15m

# Monitor performance
PYTHONPATH=src python3 src/live_simulation/monitor_performance.py
```

### **Emergency Commands:**
```bash
# Stop all processes
pkill -f "python.*trading"

# Clean everything
rm -f logs/*.log logs/*.json db/*.db

# Restart from scratch
PYTHONPATH=src python3 src/quick_health_check.py
```

---

## 📝 **Notes**

- Always use `PYTHONPATH=src` when running commands
- Check logs regularly for errors
- Backup results before major changes
- Test strategies thoroughly before live trading
- Monitor performance continuously during live trading

---

*Last Updated: $(date)*  
*Version: 1.0*  
*Status: Production Ready* ✅
