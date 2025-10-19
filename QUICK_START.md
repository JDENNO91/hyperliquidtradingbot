# 🚀 Quick Start Guide

## Run a Strategy in 3 Steps

### Step 1: Activate Environment
```bash
cd /Users/jdennis/Documents/GitHub/hyperliquidpython
source .venv/bin/activate
```

### Step 2: Choose Your Strategy

**Option A - Interactive Selector:**
```bash
python3 tools/select_strategy.py
```

**Option B - Direct Command:**
```bash
# 🏆 BEST: Highest returns (97%), lowest risk (2.94%)
python3 src/cli/backtest.py --config src/config/production/rsi_scalping/standard_5m.json
```

### Step 3: Review Results
- Check the output for trades, win rate, return, and max drawdown
- Compare with expected performance in `PRODUCTION_STRATEGIES.md`

---

## 📊 Strategy Quick Reference

| When You Want... | Use This Strategy | Trades/Day |
|------------------|-------------------|------------|
| **Best returns** | RSI Scalping Standard 5m 🏆 | 2.3 |
| **More activity** | RSI Scalping Extreme 5m | 3.6 |
| **Highest win rate** | MA+RSI Hybrid 5m | 1.4 |
| **10+ trades/day** | RSI Scalping Ultra 1m ⚠️ | 44 |

---

## 🎯 Expected Performance

| Strategy | 7-Day Return | Monthly (Est) | Max Drawdown |
|----------|--------------|---------------|--------------|
| RSI Standard 5m | 97% | 100-200% | 3-5% |
| RSI Extreme 5m | 95% | 150-250% | 5-8% |
| MA+RSI 5m | 96% | 100-180% | 3-5% |
| RSI Ultra 1m | 47% | 80-150% | 40-60% ⚠️ |

---

## 📁 File Locations

- **Production Configs:** `src/config/production/`
- **Strategy Files:** `src/strategies/core/`
- **Documentation:** `PRODUCTION_STRATEGIES.md` (detailed)
- **Quick Selector:** `select_strategy.py`
- **This Guide:** `QUICK_START.md`

---

## ⚡ One-Liner Commands

```bash
# Recommended strategy
python3 src/cli/backtest.py --config src/config/production/rsi_scalping/standard_5m.json

# More active
python3 src/cli/backtest.py --config src/config/production/rsi_scalping/extreme_5m.json

# Conservative
python3 src/cli/backtest.py --config src/config/production/ma_rsi_hybrid/standard_5m.json

# High frequency (advanced)
python3 src/cli/backtest.py --config src/config/production/rsi_scalping/ultra_1m.json
```

---

## 🔄 Next Steps After Backtesting

1. ✅ Review results
2. 📝 Paper trade for 7-14 days
3. 🔍 Run live simulation
4. 🚀 Go live with small sizes
5. 📊 Monitor and adjust

---

**Start here:** RSI Scalping Standard 5m - It has the best risk/reward ratio!

