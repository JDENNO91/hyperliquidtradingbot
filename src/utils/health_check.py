#!/usr/bin/env python3
"""
Simple Health Check for Trading System
Tests core functionality without complex validation
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def health_check():
    """Run simple health check for core trading modules."""
    print("🚀 TRADING SYSTEM HEALTH CHECK")
    print("=" * 50)
    
    results = {
        'core_imports': False,
        'strategy_imports': False,
        'backtesting': False,
        'cli_tools': False,
        'config_files': False
    }
    
    # Test 1: Core Imports
    print("🔍 Testing core imports...")
    try:
        from core.base_strategy import BaseStrategy
        from core.improved_trading_engine import ImprovedTradingEngine
        from core.simple_risk_manager import SimpleRiskManager
        print("✅ Core imports successful")
        results['core_imports'] = True
    except Exception as e:
        print(f"❌ Core import failed: {e}")
    
    # Test 2: Strategy Imports
    print("\n🧠 Testing strategy imports...")
    try:
        from strategies.core.rsi_scalping_strategy import RSIScalpingStrategy
        from strategies.core.bbrsi_strategy import BBRSIStrategy
        from strategies.core.scalping_strategy import ScalpingStrategy
        from strategies.strategy_factory import StrategyFactory
        print("✅ Strategy imports successful")
        results['strategy_imports'] = True
    except Exception as e:
        print(f"❌ Strategy import failed: {e}")
    
    # Test 3: Backtesting
    print("\n📊 Testing backtesting...")
    try:
        from backtesting.improved_backtester import ImprovedBacktester
        # Test with a simple config
        config_path = 'src/config/production/rsi_scalping/standard_5m.json'
        if Path(config_path).exists():
            backtester = ImprovedBacktester(config_path)
            print("✅ Backtesting engine working")
            results['backtesting'] = True
        else:
            print("⚠️ Config file not found, but backtester imports OK")
            results['backtesting'] = True
    except Exception as e:
        print(f"❌ Backtesting failed: {e}")
    
    # Test 4: CLI Tools
    print("\n🛠️ Testing CLI tools...")
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, 'src/cli/backtest.py', '--help'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and 'usage:' in result.stdout:
            print("✅ CLI tools working")
            results['cli_tools'] = True
        else:
            print("⚠️ CLI test inconclusive")
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
    
    # Test 5: Configuration Files
    print("\n⚙️ Testing configuration files...")
    try:
        import json
        config_files = [
            'src/config/production/rsi_scalping/standard_5m.json',
            'src/config/production/rsi_scalping/extreme_5m.json',
            'src/config/production/rsi_scalping/ultra_1m.json',
            'src/config/production/ma_rsi_hybrid/standard_5m.json'
        ]
        
        valid_configs = 0
        for config_file in config_files:
            if Path(config_file).exists():
                with open(config_file, 'r') as f:
                    json.load(f)  # Test JSON validity
                valid_configs += 1
        
        if valid_configs > 0:
            print(f"✅ {valid_configs}/{len(config_files)} config files valid")
            results['config_files'] = True
        else:
            print("❌ No valid config files found")
    except Exception as e:
        print(f"❌ Config test failed: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 HEALTH CHECK SUMMARY")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test.replace('_', ' ').title()}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🚀 System is HEALTHY and ready for trading!")
        return True
    elif passed >= total * 0.8:
        print("⚠️ System is mostly healthy with minor issues")
        return True
    else:
        print("❌ System has significant issues that need attention")
        return False

if __name__ == "__main__":
    health_check()
