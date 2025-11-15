# System Architecture

## Overview

The Hyperliquid Trading Bot is a modular, extensible trading system designed for algorithmic trading on the Hyperliquid DEX. The architecture separates concerns into distinct layers, enabling easy testing, maintenance, and extension.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Dashboard  │  │  CLI Tools   │  │   Config    │     │
│  │  (Streamlit) │  │              │  │  Manager    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Execution Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Backtesting │  │ Live Simulation│ │ Live Trading │     │
│  │    Engine    │  │    Engine     │  │    Engine    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Strategy Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Strategy   │  │   Indicator  │  │   Strategy   │     │
│  │   Factory    │  │   Utilities  │  │   Registry   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Strategy Implementations                     │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐           │   │
│  │  │ BBRSI    │ │ Scalping  │ │ Super    │           │   │
│  │  │ Strategy │ │ Strategy  │ │ Optimized│           │   │
│  │  └──────────┘ └──────────┘ └──────────┘           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Core Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Trading    │  │   Position    │  │     Risk     │     │
│  │   Engine     │  │   Manager     │  │   Manager    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                    Data & Integration Layer                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Data Loader │  │ Hyperliquid  │  │   Logging    │     │
│  │              │  │     SDK       │  │   System      │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Execution Layer

#### Backtesting Engine (`src/backtesting/improved_backtester.py`)
- **Purpose**: Historical strategy validation
- **Features**:
  - Slippage modeling
  - Transaction fee simulation
  - Order execution latency
  - Comprehensive performance metrics
- **Input**: Historical OHLCV data (JSON)
- **Output**: Performance metrics, trade history, equity curve

#### Live Simulation Engine (`src/live_simulation/`)
- **Purpose**: Paper trading with real-time market data
- **Features**:
  - Real-time market data integration
  - Simulated order execution
  - No real money risk
- **Use Case**: Strategy validation before live trading

#### Live Trading Engine (`src/live/`)
- **Purpose**: Real money trading execution
- **Features**:
  - Real order execution via Hyperliquid SDK
  - Risk management guards
  - Kill switch functionality
  - Structured logging
- **Use Case**: Production trading

### 2. Strategy Layer

#### Base Strategy (`src/core/base_strategy.py`)
- **Abstract Interface**:
  - `compute_indicators()`: Calculate technical indicators
  - `generate_signal()`: Generate trading signals
  - `evaluate_position()`: Position management logic
- **Common Features**:
  - Position tracking
  - Performance statistics
  - Configuration validation

#### Strategy Factory (`src/strategies/strategy_factory.py`)
- **Purpose**: Strategy instantiation and registration
- **Features**:
  - Dynamic strategy loading
  - Strategy discovery
  - Configuration mapping

#### Indicator Utilities (`src/strategies/indicators/`)
- **Purpose**: Reusable technical indicators
- **Available Indicators**:
  - RSI (Relative Strength Index)
  - Bollinger Bands
  - Moving Averages (SMA, EMA)
  - ADX (Average Directional Index)
  - Microprice

### 3. Core Layer

#### Trading Engine (`src/core/improved_trading_engine.py`)
- **Purpose**: Signal execution and market data processing
- **Responsibilities**:
  - Process market data
  - Execute strategy signals
  - Coordinate position and risk managers
  - Track performance

#### Position Manager (`src/core/improved_position_manager.py`)
- **Purpose**: Position lifecycle management
- **Features**:
  - Position tracking
  - Entry/exit execution
  - Position limits
  - P&L calculation

#### Risk Manager (`src/core/simple_risk_manager.py`)
- **Purpose**: Risk controls and position sizing
- **Features**:
  - Capital allocation
  - Position size limits
  - Drawdown protection
  - Maximum concurrent positions

## Data Flow

### Backtesting Flow
```
Market Data (JSON) 
    → Data Loader 
    → Backtester 
    → Trading Engine 
    → Strategy 
    → Position Manager 
    → Risk Manager 
    → Results
```

### Live Trading Flow
```
Hyperliquid API 
    → Market Data Stream 
    → Trading Engine 
    → Strategy 
    → Risk Manager (validation) 
    → Position Manager (execution) 
    → Hyperliquid Exchange 
    → Trade Logger 
    → Dashboard
```

## Configuration System

### Config Structure
```json
{
  "trading": {
    "market": "ETH-PERP",
    "timeframe": "5m",
    "leverage": 10,
    "positionSize": 0.1
  },
  "indicators": {
    "rsi_period": 14,
    "bb_period": 20
  },
  "risk_management": {
    "max_risk_per_trade": 0.02,
    "max_drawdown": 0.15,
    "stop_loss_pct": 0.015,
    "take_profit_pct": 0.03
  }
}
```

### Config Validation
- JSON Schema validation (`src/config/validator.py`)
- Required field checking
- Value range validation
- Type checking

## Strategy Switching

The system supports dynamic strategy switching:

1. **Strategy Registration**: Strategies register themselves via `StrategyFactory`
2. **Config Mapping**: Config files map to strategies
3. **Runtime Switching**: `strategy_switcher.py` updates active config
4. **Hot Reload**: Strategies can be reloaded without restart (simulation mode)

## Risk Management Pipeline

```
Signal Generated
    ↓
Risk Manager Check
    ├─ Capital Available? → No → Reject
    ├─ Max Positions? → Yes → Reject
    ├─ Risk Limits? → Exceeded → Reject
    └─ All Checks Pass → Position Manager
```

## Monitoring & Observability

### Logging Levels
- **DEBUG**: Detailed execution flow
- **INFO**: Key events (trades, signals)
- **WARNING**: Risk alerts, degraded performance
- **ERROR**: Failures, exceptions
- **CRITICAL**: Kill switch triggers

### Structured Logging
- JSON format for log aggregation
- Contextual information (strategy, market, timeframe)
- Performance metrics embedded

### Health Checks
- Component availability
- API connectivity
- Configuration validity
- Resource usage

## Extension Points

### Adding a New Strategy
1. Inherit from `BaseStrategy`
2. Implement `compute_indicators()` and `generate_signal()`
3. Register in `StrategyFactory`
4. Create config file

### Adding a New Asset/Pair
1. Add market data to `src/backtesting/data/`
2. Update config with new market symbol
3. Test with backtesting engine
4. Validate with live simulation

### Adding a New Indicator
1. Add to `src/strategies/indicators/`
2. Document parameters
3. Add unit tests
4. Update indicator utilities

## Security Considerations

### Credential Management
- Environment variables (`.env` file)
- Never commit credentials
- Production: Use secrets management (Vault, AWS Secrets Manager)

### API Security
- Rate limiting
- Error handling
- Connection retry logic
- Kill switch on API failures

### Risk Guards
- Maximum drawdown limits
- Position size limits
- Daily loss limits
- Margin usage monitoring

## Performance Considerations

### Backtesting Optimization
- Vectorized operations where possible
- Efficient data structures
- Parallel processing for walk-forward testing

### Live Trading Optimization
- Minimal latency in signal generation
- Efficient market data processing
- Connection pooling for API calls

## Testing Strategy

### Unit Tests
- Individual components
- Strategy logic
- Indicator calculations

### Integration Tests
- End-to-end backtesting
- Strategy + Risk Manager
- Position lifecycle

### Performance Tests
- Large dataset handling
- Memory usage
- Execution speed

### Live Simulation Tests
- Real market data
- Order execution simulation
- Risk management validation


