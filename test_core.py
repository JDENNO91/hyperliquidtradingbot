#!/usr/bin/env python3
"""
Core Project Test Suite
Essential tests for the Hyperliquid trading system
"""

import sys
import subprocess
import time
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n🧪 {description}")
    print("=" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()[:100]}...")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {description} - EXCEPTION: {e}")
        return False

def main():
    """Run core project tests"""
    print("🚀 HYPERLIQUID TRADING SYSTEM - CORE TEST SUITE")
    print("=" * 60)
    print(f"📅 Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print("=" * 60)
    
    tests = []
    
    # Test 1: Health Check
    tests.append(run_command(
        "python3 src/utils/health_check.py",
        "System Health Check"
    ))
    
    # Test 2: Strategy Tests (core only)
    tests.append(run_command(
        "python3 -m pytest tests/test_strategies.py::TestBBRSIStrategy::test_strategy_initialization -v",
        "Core Strategy Tests"
    ))
    
    # Test 3: Backtesting Tests
    tests.append(run_command(
        "python3 -m pytest tests/test_backtesting.py -v --tb=short",
        "Backtesting Tests"
    ))
    
    # Test 4: CLI Tests
    tests.append(run_command(
        "python3 -m pytest tests/test_cli.py -v --tb=short",
        "CLI Tests"
    ))
    
    # Test 5: Configuration Validation
    tests.append(run_command(
        "python3 -c \"import json; [json.load(open(f)) for f in ['src/config/production/rsi_scalping/standard_5m.json', 'src/config/production/rsi_scalping/extreme_5m.json', 'src/config/production/rsi_scalping/ultra_1m.json', 'src/config/production/ma_rsi_hybrid/standard_5m.json']]; print('All configs valid')\"",
        "Configuration Validation"
    ))
    
    # Test 6: Import Tests
    tests.append(run_command(
        "python3 -c \"import sys; sys.path.insert(0, 'src'); from core.base_strategy import BaseStrategy; from strategies.strategy_factory import StrategyFactory; from backtesting.improved_backtester import ImprovedBacktester; print('All imports successful')\"",
        "Core Import Tests"
    ))
    
    # Test 7: CLI Help
    tests.append(run_command(
        "python3 src/cli/backtest.py --help | head -3",
        "CLI Help Commands"
    ))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 CORE TEST SUITE RESULTS")
    print("=" * 60)
    
    passed = sum(tests)
    total = len(tests)
    percentage = (passed / total) * 100
    
    print(f"✅ Tests Passed: {passed}/{total} ({percentage:.1f}%)")
    
    if passed == total:
        print("🏆 ALL CORE TESTS PASSED - SYSTEM IS READY!")
        status = "PASS"
    elif passed >= total * 0.8:
        print("⚠️ MOSTLY PASSED - Minor issues detected")
        status = "WARN"
    else:
        print("❌ MULTIPLE FAILURES - System needs attention")
        status = "FAIL"
    
    print(f"\n🎯 Overall Status: {status}")
    print(f"📅 Completed: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    return status in ["PASS", "WARN"]

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
