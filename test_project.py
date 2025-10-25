#!/usr/bin/env python3
"""
Master Project Test Suite
Comprehensive testing for the entire Hyperliquid trading system
"""

import sys
import subprocess
import time
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n🧪 {description}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()[:100]}...")
            return True
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()[:200]}...")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {description} - EXCEPTION: {e}")
        return False

def main():
    """Run comprehensive project tests"""
    print("🚀 HYPERLIQUID TRADING SYSTEM - MASTER TEST SUITE")
    print("=" * 70)
    print(f"📅 Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"📁 Project: {Path.cwd()}")
    print("=" * 70)
    
    tests = []
    
    # Test 1: Health Check
    tests.append(run_command(
        "python3 src/utils/health_check.py",
        "System Health Check"
    ))
    
    # Test 2: Core Strategy Tests
    tests.append(run_command(
        "python3 -m pytest tests/test_strategies.py -v --tb=short",
        "Strategy Tests"
    ))
    
    # Test 3: Integration Tests
    tests.append(run_command(
        "python3 -m pytest tests/test_integration.py -v --tb=short",
        "Integration Tests"
    ))
    
    # Test 4: Backtesting Tests
    tests.append(run_command(
        "python3 -m pytest tests/test_backtesting.py -v --tb=short",
        "Backtesting Tests"
    ))
    
    # Test 5: CLI Tests
    tests.append(run_command(
        "python3 -m pytest tests/test_cli.py -v --tb=short",
        "CLI Tests"
    ))
    
    # Test 6: Risk Management Tests
    tests.append(run_command(
        "python3 -m pytest tests/test_risk_management.py -v --tb=short",
        "Risk Management Tests"
    ))
    
    # Test 7: Performance Tests
    tests.append(run_command(
        "python3 -m pytest tests/test_performance.py -v --tb=short",
        "Performance Tests"
    ))
    
    # Test 8: Configuration Validation
    tests.append(run_command(
        "python3 -c \"import json; [json.load(open(f)) for f in ['src/config/production/rsi_scalping/standard_5m.json', 'src/config/production/rsi_scalping/extreme_5m.json', 'src/config/production/rsi_scalping/ultra_1m.json', 'src/config/production/ma_rsi_hybrid/standard_5m.json']]; print('All configs valid')\"",
        "Configuration Validation"
    ))
    
    # Test 9: Import Tests
    tests.append(run_command(
        "python3 -c \"import sys; sys.path.insert(0, 'src'); from core.base_strategy import BaseStrategy; from strategies.strategy_factory import StrategyFactory; from backtesting.improved_backtester import ImprovedBacktester; print('All imports successful')\"",
        "Core Import Tests"
    ))
    
    # Test 10: CLI Help Tests
    tests.append(run_command(
        "python3 src/cli/backtest.py --help | head -5",
        "CLI Help Commands"
    ))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 MASTER TEST SUITE RESULTS")
    print("=" * 70)
    
    passed = sum(tests)
    total = len(tests)
    percentage = (passed / total) * 100
    
    print(f"✅ Tests Passed: {passed}/{total} ({percentage:.1f}%)")
    
    if passed == total:
        print("🏆 ALL TESTS PASSED - SYSTEM IS PRODUCTION READY!")
        status = "PASS"
    elif passed >= total * 0.8:
        print("⚠️ MOSTLY PASSED - Minor issues detected")
        status = "WARN"
    else:
        print("❌ MULTIPLE FAILURES - System needs attention")
        status = "FAIL"
    
    print(f"\n🎯 Overall Status: {status}")
    print(f"📅 Completed: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    return status == "PASS"

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
