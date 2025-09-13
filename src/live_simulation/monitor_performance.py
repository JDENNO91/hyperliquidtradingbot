#!/usr/bin/env python3
"""
Live Simulation Performance Monitor

Real-time monitoring of live simulation performance, similar to how backtester shows results.
"""

import sys
import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.live_simulation.live_simulation_trade_statistics import LiveSimulationTradeStatistics

class PerformanceMonitor:
    """Real-time performance monitoring for live simulation."""
    
    def __init__(self):
        self.logs_dir = Path(__file__).parent.parent / "logs"
        self.trades_file = self.logs_dir / "live_simulation_trades.json"
        self.stats_file = self.logs_dir / "live_simulation_trade_statistics.json"
        self.debug_log = self.logs_dir / "live_simulation_debug.log"
        
    def get_current_position_status(self) -> Dict[str, Any]:
        """Extract current position status from debug log."""
        try:
            with open(self.debug_log, 'r') as f:
                lines = f.readlines()
            
            # Look for the most recent position information
            position_info = {}
            for line in reversed(lines[-100:]):  # Check last 100 lines
                if "Simulated Value=" in line:
                    # Extract position metrics
                    parts = line.split("Simulated Value=")[1].split(",")
                    position_info["simulated_value"] = float(parts[0])
                    position_info["account"] = float(parts[1].split("=")[1])
                    position_info["unrealized_pnl"] = float(parts[2].split("=")[1])
                    position_info["peak"] = float(parts[3].split("=")[1])
                    position_info["drawdown"] = float(parts[4].split("=")[1].replace("%", ""))
                    position_info["timestamp"] = line.split(" - ")[0]
                    break
                    
            return position_info
        except Exception as e:
            return {"error": f"Failed to read position status: {e}"}
    
    def get_trade_statistics(self) -> Dict[str, Any]:
        """Get current trade statistics."""
        try:
            if not self.trades_file.exists():
                return {"total_trades": 0, "message": "No trades recorded yet"}
            
            with open(self.trades_file, 'r') as f:
                trades = json.load(f)
            
            if not trades:
                return {"total_trades": 0, "message": "No trades recorded yet"}
            
            stats_analyzer = LiveSimulationTradeStatistics(trades)
            return stats_analyzer.get_current_performance_summary()
            
        except Exception as e:
            return {"error": f"Failed to read trade statistics: {e}"}
    
    def get_recent_activity(self) -> Dict[str, Any]:
        """Get recent activity from debug log."""
        try:
            with open(self.debug_log, 'r') as f:
                lines = f.readlines()
            
            recent_lines = lines[-20:]  # Last 20 lines
            activity = {
                "latest_candle": None,
                "latest_signal": None,
                "latest_error": None,
                "last_update": None
            }
            
            for line in reversed(recent_lines):
                if "Latest candle (close):" in line:
                    activity["latest_candle"] = line.strip()
                    if not activity["last_update"]:
                        activity["last_update"] = line.split(" - ")[0]
                elif "Signal:" in line and "NONE" not in line:
                    activity["latest_signal"] = line.strip()
                elif "ERROR" in line or "WARNING" in line:
                    activity["latest_error"] = line.strip()
            
            return activity
            
        except Exception as e:
            return {"error": f"Failed to read recent activity: {e}"}
    
    def display_performance_summary(self):
        """Display a comprehensive performance summary."""
        print("\n" + "="*80)
        print("LIVE SIMULATION PERFORMANCE MONITOR")
        print("="*80)
        
        # Current position status
        position = self.get_current_position_status()
        if "error" not in position:
            print(f"\n📊 CURRENT POSITION STATUS")
            print(f"   Timestamp: {position.get('timestamp', 'N/A')}")
            print(f"   Simulated Value: ${position.get('simulated_value', 0):.2f}")
            print(f"   Account Balance: ${position.get('account', 0):.2f}")
            print(f"   Unrealized PnL: ${position.get('unrealized_pnl', 0):.2f}")
            print(f"   Peak Value: ${position.get('peak', 0):.2f}")
            print(f"   Current Drawdown: {position.get('drawdown', 0):.2f}%")
        else:
            print(f"\n❌ POSITION STATUS ERROR: {position['error']}")
        
        # Trade statistics
        stats = self.get_trade_statistics()
        if "error" not in stats:
            print(f"\n📈 TRADE PERFORMANCE")
            print(f"   Total Trades: {stats.get('total_trades', 0)}")
            print(f"   Win Rate: {stats.get('win_rate', 0):.2%}")
            print(f"   Total PnL: ${stats.get('total_pnl', 0):.2f}")
            print(f"   Average PnL: ${stats.get('average_pnl', 0):.2f}")
            print(f"   Max Win: ${stats.get('max_win', 0):.2f}")
            print(f"   Max Loss: ${stats.get('max_loss', 0):.2f}")
            print(f"   Current Streak: {stats.get('current_streak', 0)}")
            
            if stats.get('best_day'):
                print(f"   Best Day: {stats['best_day']}")
            if stats.get('worst_day'):
                print(f"   Worst Day: {stats['worst_day']}")
        else:
            print(f"\n❌ TRADE STATISTICS ERROR: {stats['error']}")
        
        # Recent activity
        activity = self.get_recent_activity()
        if "error" not in activity:
            print(f"\n🔄 RECENT ACTIVITY")
            if activity.get('latest_candle'):
                print(f"   {activity['latest_candle']}")
            if activity.get('latest_signal'):
                print(f"   {activity['latest_signal']}")
            if activity.get('latest_error'):
                print(f"   ⚠️  {activity['latest_error']}")
            if activity.get('last_update'):
                print(f"   Last Update: {activity['last_update']}")
        else:
            print(f"\n❌ ACTIVITY ERROR: {activity['error']}")
        
        print("\n" + "="*80)
    
    def monitor_continuously(self, interval_seconds: int = 30):
        """Continuously monitor performance with auto-refresh."""
        try:
            while True:
                os.system('clear' if os.name == 'posix' else 'cls')
                self.display_performance_summary()
                print(f"\n🔄 Auto-refreshing every {interval_seconds} seconds... (Press Ctrl+C to stop)")
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n\n✅ Monitoring stopped by user")

def main():
    """Main entry point."""
    monitor = PerformanceMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        monitor.monitor_continuously()
    else:
        monitor.display_performance_summary()

if __name__ == "__main__":
    main()
