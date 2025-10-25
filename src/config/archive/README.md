# 📁 Archive Configuration Files

This directory contains historical configuration files that are no longer in active use but are kept for reference.

## 📂 **Organization**

### **ma_crossover/** - Moving Average Crossover Strategies
- `backtest_ma_crossover_eth.json` - Original MA crossover
- `backtest_ma_crossover_balanced_eth.json` - Balanced variant
- `backtest_ma_crossover_eth_15m.json` - 15-minute timeframe
- `backtest_ma_crossover_eth_1h.json` - 1-hour timeframe
- `backtest_ma_crossover_fast_eth.json` - Fast variant
- `backtest_ma_crossover_optimized_eth.json` - Optimized variant
- `backtest_ma_rsi_hybrid_5m_btc.json` - MA+RSI hybrid for BTC
- `backtest_ma_rsi_hybrid_5m_eth.json` - MA+RSI hybrid for ETH

### **rsi_scalping/** - RSI Scalping Strategies
- `backtest_rsi_scalping_1m_eth.json` - 1-minute RSI scalping
- `backtest_rsi_scalping_5m_eth.json` - 5-minute RSI scalping
- `backtest_rsi_scalping_extreme_5m_eth.json` - Extreme variant
- `backtest_rsi_scalping_ultra_5m_eth.json` - Ultra variant

### **zscore/** - Z-Score Mean Reversion Strategies
- `backtest_zscore_btc_5m_24h.json` - BTC 5-minute Z-score
- `backtest_zscore_eth_5m_24h.json` - ETH 5-minute Z-score
- `backtest_zscore_eth.json` - Original ETH Z-score

### **high_frequency/** - High Frequency Trading
- `backtest_high_freq_1m_eth.json` - 1-minute high frequency
- `backtest_high_freq_5m_eth.json` - 5-minute high frequency

### **mtf_momentum/** - Multi-Timeframe Momentum
- `backtest_mtf_momentum_eth.json` - Multi-timeframe momentum strategy

## ⚠️ **Important Notes**

- **These configs are ARCHIVED** - Do not use for production
- **Use production configs** in `../production/` instead
- **These are kept for reference** and historical analysis
- **Performance may vary** from current production strategies

## 🔄 **Migration to Production**

If you need to use any of these strategies:
1. Review the archived config
2. Test with current backtesting engine
3. If profitable, move to `../production/` directory
4. Update with current best practices

## 📊 **Why Archived?**

- **Lower performance** compared to production strategies
- **Outdated parameters** not optimized for current market
- **Replaced by better variants** in production folder
- **Kept for reference** and potential future optimization

---

*Last Updated: October 25, 2025*
