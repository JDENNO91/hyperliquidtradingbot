# 🚀 Hyperliquid SDK Guide

## 📚 **What This Folder Contains**

The `hyperliquid_sdk/` folder contains the **official Hyperliquid Python SDK** with:
- **API Documentation** - How to interact with Hyperliquid
- **Code Examples** - Working examples of all operations
- **Test Cases** - How to test your implementations
- **Best Practices** - Recommended usage patterns

## 🎯 **Why It's Useful for Your Trading Bot**

### **✅ What You Get:**
1. **API Reference** - All available methods and parameters
2. **Working Examples** - Copy-paste code that actually works
3. **Error Handling** - How to handle common API issues
4. **Best Practices** - Avoid common pitfalls
5. **Testing** - Verify your implementations work correctly

### **🔍 Key SDK Components:**

#### **1. Info Client (`hyperliquid.info.Info`)**
```python
from hyperliquid.info import Info

# Get market data, order book, user positions
info = Info(base_url="https://api.hyperliquid.xyz")

# Get all markets
markets = info.meta()

# Get order book for a symbol
orderbook = info.order_book("BTC-PERP")

# Get user positions
positions = info.user_state(account_address)
```

#### **2. Exchange Client (`hyperliquid.exchange.Exchange`)**
```python
from hyperliquid.exchange import Exchange

# Place orders, manage positions
exchange = Exchange(
    private_key="your_private_key",
    base_url="https://api.hyperliquid.xyz",
    account_address="your_address"
)

# Place a market order
order = exchange.order(
    symbol="BTC-PERP",
    side="B",
    size=0.1,
    order_type="Market"
)

# Cancel an order
exchange.cancel_order(order_id)
```

## 📖 **Essential SDK Operations**

### **🔍 Market Data Operations:**
```python
# Get real-time market data
info = Info(base_url="https://api.hyperliquid.xyz")

# Get all available markets
markets = info.meta()
print(f"Available markets: {[m['name'] for m in markets]}")
```

### **💰 Trading Operations:**
```python
# Place a limit order
exchange = Exchange(private_key=key, base_url=url, account_address=addr)

order = exchange.order(
    symbol="BTC-PERP",
    side="B",  # B = Buy, A = Sell
    size=0.01,  # Size in base currency
    order_type="Limit",
    price=50000.0  # Limit price
)
```

### **📊 Position Management:**
```python
# Get current positions
positions = info.user_state(account_address)

# Check if you have open positions
for pos in positions['assetPositions']:
    if pos['position'] != 0:
        print(f"Position in {pos['name']}: {pos['position']}")
```

## 🛠️ **Common Use Cases for Your Bot**

### **1. Market Data Collection:**
```python
def get_market_data(symbol: str):
    """Get real-time market data for a symbol."""
    info = Info(base_url="https://api.hyperliquid.xyz")
    
    # Get order book
    orderbook = info.order_book(symbol)
    
    # Get recent trades
    trades = info.trades(symbol)
    
    # Get market meta
    meta = info.meta()
    
    return {
        'orderbook': orderbook,
        'trades': trades,
        'meta': meta
    }
```

### **2. Position Monitoring:**
```python
def monitor_positions(account_address: str):
    """Monitor current positions and PnL."""
    info = Info(base_url="https://api.hyperliquid.xyz")
    
    # Get user state
    user_state = info.user_state(account_address)
    
    # Extract positions
    positions = []
    for pos in user_state['assetPositions']:
        if pos['position'] != 0:
            positions.append({
                'symbol': pos['name'],
                'size': pos['position'],
                'entry_price': pos['entryPrice'],
                'unrealized_pnl': pos['unrealizedPnl']
            })
    
    return positions
```

### **3. Order Management:**
```python
def place_trade_order(symbol: str, side: str, size: float, order_type: str, price: float = None):
    """Place a trade order with proper error handling."""
    try:
        exchange = Exchange(
            private_key=os.getenv("HL_PRIVATE_KEY"),
            base_url=os.getenv("HL_API_URL"),
            account_address=os.getenv("HL_ADDRESS")
        )
        
        order_params = {
            'symbol': symbol,
            'side': side,  # 'B' for buy, 'A' for sell
            'size': size,
            'order_type': order_type
        }
        
        if order_type == "Limit" and price:
            order_params['price'] = price
        
        # Place the order
        result = exchange.order(**order_params)
        
        print(f"Order placed successfully: {result}")
        return result
        
    except Exception as e:
        print(f"Failed to place order: {e}")
        return None
```

## 📁 **SDK Folder Structure**

```
hyperliquid_sdk/
├── hyperliquid/          # Main SDK code
│   ├── info.py          # Market data operations
│   ├── exchange.py      # Trading operations
│   └── utils.py         # Utility functions
├── examples/             # Working examples
│   ├── basic_usage.py   # Basic SDK usage
│   ├── trading.py       # Trading examples
│   └── websocket.py     # Real-time data
├── tests/               # Test cases
├── README.md            # SDK documentation
└── pyproject.toml       # Dependencies
```

## 🚨 **Important Notes**

### **⚠️ Don't Import From This Folder:**
```python
# ❌ WRONG - Don't do this
from src.application.hyperliquid_sdk.hyperliquid.info import Info

# ✅ CORRECT - Use the installed package
from hyperliquid.info import Info
```

### **✅ Use This Folder For:**
- **Reading documentation**
- **Copying examples**
- **Understanding API usage**
- **Testing your implementations**
- **Learning best practices**

## 🔗 **Quick Reference Links**

- **SDK Documentation**: `hyperliquid_sdk/README.md`
- **Code Examples**: `hyperliquid_sdk/examples/`
- **API Reference**: `hyperliquid_sdk/hyperliquid/`
- **Test Cases**: `hyperliquid_sdk/tests/`

## 💡 **Pro Tips**

1. **Start with examples** - Copy working code from `examples/` folder
2. **Check test cases** - See how the SDK is supposed to work
3. **Read the README** - Understand the overall architecture
4. **Use error handling** - Always wrap API calls in try-catch
5. **Test with small amounts** - Verify everything works before going live

---

**This SDK folder is your reference library - use it to understand how to interact with Hyperliquid effectively!** 📚✨
