# 🔐 Hyperliquid Credentials Setup Guide

This guide explains how to set up your Hyperliquid credentials for live trading and what works without credentials.

## 📋 **Quick Overview**

| Feature | Requires Credentials? | Description |
|---------|---------------------|-------------|
| **Backtesting** | ❌ No | Historical simulation with saved data |
| **Live Simulation** | ❌ No | Paper trading with live market data |
| **Live Trading** | ✅ Yes | Real money trading on Hyperliquid |

## 🚀 **Quick Start (No Credentials Needed)**

You can start using the bot immediately without any credentials:

```bash
# Run backtesting (no credentials needed)
python3 -m src.cli.backtest --config src/config/production/rsi_scalping/backtest_eth.json

# Run live simulation (no credentials needed)
python3 -m src.cli.simulate --profile live_eth

# Check system health
python3 src/utils/health_check.py
```

## 🔧 **Setting Up Credentials (For Live Trading)**

### **Step 1: Create Environment File**
```bash
# Copy the template
cp config/env.template .env

# Edit with your actual credentials
nano .env
```

### **Step 2: Add Your Hyperliquid Credentials**
Edit the `.env` file with your actual credentials:

```bash
# Hyperliquid API Configuration
HL_API_URL=https://api.hyperliquid.xyz

# Your Hyperliquid Private Key (keep this secret!)
HL_PRIVATE_KEY=0x1234567890abcdef...

# Your Hyperliquid Wallet Address
HL_ADDRESS=0xabcdef1234567890...
```

### **Step 3: Verify Your Setup**
```bash
# Check your credential setup
python3 check_credentials.py
```

**Expected Output:**
```
✅ Market Data Access: AVAILABLE
✅ Live Trading: AVAILABLE (if credentials are valid)
```

## 🔍 **Understanding the Output**

### **✅ Market Data Access: AVAILABLE**
- ✅ You can run **live simulation** (paper trading)
- ✅ You can run **backtesting**
- ✅ You can test strategies with live market data

### **✅ Live Trading: AVAILABLE**
- ✅ You can run **live trading** (real money)
- ⚠️ **WARNING**: This uses real money!

### **❌ Missing Credentials**
- ❌ Live trading won't work
- ✅ Live simulation still works
- ✅ Backtesting still works

## 🛡️ **Security Best Practices**

### **Keep Your Credentials Safe:**
1. **Never commit `.env` to git** (already in `.gitignore`)
2. **Use strong, unique private keys**
3. **Don't share your credentials**
4. **Rotate keys regularly**

### **Test Before Live Trading:**
```bash
# Always test with simulation first
python3 -m src.cli.simulate --profile live_eth

# Then test with dry-run mode
python3 -m src.cli.trade --profile live_eth --dry-run
```

## 🚨 **Troubleshooting**

### **"Missing environment variables" Error**
```bash
# Check if .env file exists
ls -la .env

# If missing, create it
cp config/env.template .env
nano .env
```

### **"Hyperliquid API connection failed" Error**
- Check your internet connection
- Verify Hyperliquid API is accessible
- Check if you're behind a firewall

### **"Trading credentials test failed" Error**
- Verify your private key is correct
- Check your wallet address
- Ensure you have funds in your Hyperliquid account

## 📞 **Getting Help**

### **Check System Status:**
```bash
# Full system health check
python3 src/utils/health_check.py

# Credential-specific check
python3 check_credentials.py

# Run all tests
python3 test_core.py
```

### **Common Commands:**
```bash
# Backtesting (no credentials needed)
python3 -m src.cli.backtest --config src/config/production/rsi_scalping/backtest_eth.json

# Live simulation (no credentials needed)
python3 -m src.cli.simulate --profile live_eth

# Live trading (requires credentials)
python3 -m src.cli.trade --profile live_eth --dry-run
```

## 🎯 **Next Steps**

1. **Start with Backtesting** - Test strategies with historical data
2. **Try Live Simulation** - Paper trade with live market data
3. **Set Up Credentials** - When ready for live trading
4. **Start Small** - Begin with small amounts for live trading

---

**💡 Remember: You can use most features without credentials! Start with backtesting and live simulation to test your strategies safely.**
