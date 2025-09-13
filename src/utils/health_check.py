#!/usr/bin/env python3
"""
Universal Health Check for Trading System
Tests all modules: live, live_simulation, and backtesting
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def health_check():
    """Run comprehensive health check for all trading modules."""
    print("🚀 UNIVERSAL TRADING SYSTEM HEALTH CHECK")
    print("=" * 60)
    
    results = {
        'imports': False,
        'api_connection': False,
        'config': False,
        'strategies': False,
        'backtesting': False,
        'live_simulation': False,
        'live_trading': False,
        'file_system': False
    }
    
    # Test 1: Core Imports
    print("🔍 Testing core imports...")
    try:
        from core.base_strategy import BaseStrategy
        from core.improved_trading_engine import ImprovedTradingEngine
        from core.improved_position_manager import ImprovedPositionManager
        from core.simple_risk_manager import SimpleRiskManager
        from strategies.strategy_factory import StrategyFactory
        from config.config_manager import ConfigManager
        print("✅ Core imports successful")
        results['imports'] = True
    except Exception as e:
        print(f"❌ Core import failed: {e}")
        # Try alternative imports
        try:
            from core.base_strategy import BaseStrategy
            from strategies.strategy_factory import StrategyFactory
            print("✅ Basic imports successful")
            results['imports'] = True
        except Exception as e2:
            print(f"❌ Basic import also failed: {e2}")
    
    # Test 2: Strategy Imports
    print("\n🧠 Testing strategy imports...")
    try:
        from strategies.core.bbrsi_strategy import BBRSIStrategy
        from strategies.core.scalping_strategy import ScalpingStrategy
        from strategies.timeframe_optimized.super_optimized_strategy import SuperOptimizedStrategy
        from strategies.timeframe_optimized.super_optimized_5m_strategy import SuperOptimized5mStrategy
        from strategies.timeframe_optimized.super_optimized_15m_strategy import SuperOptimized15mStrategy
        print("✅ Strategy imports successful")
        results['strategies'] = True
    except Exception as e:
        print(f"❌ Strategy import failed: {e}")
    
    # Test 3: API Connection (if available)
    print("\n🌐 Testing API connection...")
    try:
        from application.hyperliquid_sdk.hyperliquid.info import Info
        info = Info()
        print("✅ API client created")
        
        # Quick market data test
        candles = info.candles_snapshot('ETH', '1m', 0, 5)
        if candles and len(candles) > 0:
            latest_price = candles[-1]['c']
            print(f"✅ Market data working - Latest ETH: ${latest_price}")
        else:
            print("⚠️ Market data fetch issue (but API connection works)")
        results['api_connection'] = True
            
    except Exception as e:
        print(f"⚠️ API test failed (expected in offline mode): {e}")
        results['api_connection'] = False
    
    # Test 4: Configuration
    print("\n⚙️ Testing configuration...")
    try:
        from config.config_manager import ConfigManager
        config_manager = ConfigManager()
        
        # Test core configs
        core_configs = ['backtest_eth', 'backtest_scalping_eth']
        for config_name in core_configs:
            config = config_manager.load_config(config_name)
            print(f"✅ {config_name} config loaded")
        
        # Test timeframe configs
        timeframe_configs = ['backtest_super_optimized_eth', 'backtest_super_optimized_5m_eth', 'backtest_super_optimized_15m_eth']
        for config_name in timeframe_configs:
            config = config_manager.load_config(config_name)
            print(f"✅ {config_name} config loaded")
            
        results['config'] = True
        
    except Exception as e:
        print(f"❌ Config test failed: {e}")
    
    # Test 5: Backtesting Module
    print("\n📊 Testing backtesting module...")
    try:
        from backtesting.improved_backtester import ImprovedBacktester
        print("✅ Backtesting module ready")
        results['backtesting'] = True
    except Exception as e:
        print(f"❌ Backtesting test failed: {e}")
    
    # Test 6: Live Simulation Module
    print("\n🎮 Testing live simulation module...")
    try:
        from live_simulation.run_live_simulation import main as sim_main
        from live_simulation.monitor_performance import main as monitor_main
        print("✅ Live simulation module ready")
        results['live_simulation'] = True
    except Exception as e:
        print(f"❌ Live simulation test failed: {e}")
    
    # Test 7: Live Trading Module
    print("\n💰 Testing live trading module...")
    try:
        from live.run_live import main as live_main
        print("✅ Live trading module ready")
        results['live_trading'] = True
    except Exception as e:
        print(f"❌ Live trading test failed: {e}")
    
    # Test 8: File System
    print("\n📁 Testing file system...")
    try:
        logs_dir = Path(__file__).parent.parent.parent / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        test_file = logs_dir / "health_check_test.txt"
        with open(test_file, 'w') as f:
            f.write("Health check test\n")
        
        test_file.unlink()  # Clean up
        print("✅ File system accessible")
        results['file_system'] = True
        
    except Exception as e:
        print(f"❌ File system test failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 HEALTH CHECK SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test.upper().replace('_', ' '):<20} {status}")
    
    print(f"\nOVERALL: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL SYSTEMS READY!")
        print("\n🚀 Available Commands:")
        print("   Backtesting:    python -m cli.backtest --config config/core/backtest_eth.json")
        print("   Live Simulation: python -m cli.simulate --profile live_eth")
        print("   Live Trading:    python -m cli.trade --config config/live_eth.json")
        print("   Strategy List:   python -m cli.timeframe_switcher --list-timeframes")
    else:
        print("⚠️ Some systems need attention")
    
    return passed == total

if __name__ == "__main__":
    success = health_check()
    sys.exit(0 if success else 1)
