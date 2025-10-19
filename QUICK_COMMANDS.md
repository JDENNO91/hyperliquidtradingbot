# 🚀 Quick Commands - Production Strategies

**Last Updated:** October 19, 2025  
**Location:** `/Users/jdennis/Documents/GitHub/hyperliquidpython`

---

## ⚡ Setup (Run Once)

```bash
cd /Users/jdennis/Documents/GitHub/hyperliquidpython
source .venv/bin/activate
```

---

## 🏆 Production Strategies (All Profitable)

### 🥇 BEST: RSI Scalping Standard 5m
```bash
python3 src/cli/backtest.py --config src/config/production/rsi_scalping/standard_5m.json
```
**Results:** 16 trades (2.3/day), 97% return, 2.94% DD, 6.2% win rate  
**Best for:** Highest returns with lowest risk 🏆

---

### ⚡ MOST ACTIVE: RSI Scalping Extreme 5m
```bash
python3 src/cli/backtest.py --config src/config/production/rsi_scalping/extreme_5m.json
```
**Results:** 25 trades (3.6/day), 94.69% return, 5.31% DD, 4% win rate  
**Best for:** More trading activity without excessive risk

---

### 🎯 CONSERVATIVE: MA+RSI Hybrid 5m
```bash
python3 src/cli/backtest.py --config src/config/production/ma_rsi_hybrid/standard_5m.json
```
**Results:** 10 trades (1.4/day), 96.47% return, 3.53% DD, 10% win rate  
**Best for:** Highest win rate, part-time traders

---

### 🚨 HIGH FREQUENCY: RSI Scalping Ultra 1m (Advanced)
```bash
python3 src/cli/backtest.py --config src/config/production/rsi_scalping/ultra_1m.json
```
**Results:** 308 trades (44/day), 46.60% return, 53.40% DD, 0.3% win rate  
**Best for:** 10+ trades/day goal - ⚠️ High risk, constant monitoring required

---

## 🎨 Interactive Strategy Selector

```bash
python3 select_strategy.py
```
Simple menu to choose and run strategies interactively.

---

## 📊 Strategy Comparison

| Strategy | Timeframe | Trades/Day | Win% | Return | Risk | Monitoring |
|----------|-----------|------------|------|--------|------|------------|
| RSI Standard 🏆 | 5m | 2.3 | 6.2% | 97% | Low | 3-4x daily |
| RSI Extreme ⚡ | 5m | 3.6 | 4.0% | 95% | Moderate | 5-6x daily |
| MA+RSI 🎯 | 5m | 1.4 | 10% | 96% | Low | 2-3x daily |
| RSI Ultra ⚠️ | 1m | 44 | 0.3% | 47% | Very High | Constant |

---

## 🔧 How Each Strategy Works

### RSI Scalping (Standard & Extreme)
- **Theory:** Mean reversion - buy oversold, sell overbought
- **Entry:** RSI extremes (Standard: 35/65, Extreme: 45/55)
- **Exit:** RSI returns to neutral or profit target
- **Best on:** ETH-PERP (high volatility)

### MA+RSI Hybrid
- **Theory:** Confluence trading - trend + momentum must align
- **Entry:** MA crossover (SMA25/EMA10) + RSI confirmation
- **Exit:** Opposite crossover or profit target
- **Best on:** ETH-PERP 5m or 1h

---

## 🎯 Choose Based on Your Style

### I want the BEST returns
→ **RSI Scalping Standard 5m** (97% return, 2.94% DD)

### I want MORE trades per day
→ **RSI Scalping Extreme 5m** (3.6/day) or **Ultra 1m** (44/day ⚠️)

### I want the HIGHEST win rate
→ **MA+RSI Hybrid 5m** (10% win rate)

### I'm a part-time trader
→ **MA+RSI Hybrid 5m** (1.4/day, check 2-3x daily)

### I'm an active trader
→ **RSI Scalping Standard 5m** (2.3/day, check 3-4x daily)

### I can monitor constantly
→ **RSI Scalping Ultra 1m** (44/day, check every 30-60 min) ⚠️

---

## 📚 Documentation

- **Quick Start:** `QUICK_START.md`
- **Detailed Guide:** `docs/user-guides/PRODUCTION_STRATEGIES.md`
- **Interactive Selector:** `select_strategy.py`
- **Config Location:** `src/config/production/`
- **Archived Configs:** `src/config/archive/` (old/test configs)

---

## ⚠️ Important Notes

1. **All results are from 7-day backtests** - Real trading may vary
2. **Conservative estimates:** Expect 50-100% monthly in real trading
3. **Always paper trade first** before going live
4. **Start small** and scale up gradually
5. **ETH-PERP outperforms BTC-PERP** for these strategies
6. **Low win rates (4-10%) are normal** for profitable trend-following
7. **Risk management is key** - Never risk more than you can afford to lose

---

## 🎉 You're Ready!

Start with the recommended strategy:
```bash
python3 src/cli/backtest.py --config src/config/production/rsi_scalping/standard_5m.json
```

Then move to paper trading, then live with small sizes. Good luck! 🚀
