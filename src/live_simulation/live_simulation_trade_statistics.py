"""Module for analyzing live simulated trades and recording trade statistics."""

import os
import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional

class LiveSimulationTradeStatistics:
    """
    Analyzes and records statistics from live simulated trading sessions.
    Computes summary metrics including win/loss count, averages, 
    max/min PnL, and breakdown by exit reason.
    """

    def __init__(self, trades: Optional[List[Dict[str, Any]]] = None):
        """
        Initialize with an optional list of trades.

        Args:
            trades (list, optional): List of trade dictionaries. Defaults to empty list.
        """
        self.trades = trades or []

    def get_current_performance_summary(self) -> Dict[str, Any]:
        """
        Get a quick performance summary for real-time monitoring.
        
        Returns:
            dict: Current performance metrics
        """
        if not self.trades:
            return {
                "total_trades": 0,
                "win_rate": 0.0,
                "total_pnl": 0.0,
                "average_pnl": 0.0,
                "max_win": 0.0,
                "max_loss": 0.0,
                "current_streak": 0,
                "best_day": None,
                "worst_day": None
            }
        
        # Calculate basic metrics
        total_trades = len(self.trades)
        profitable_trades = sum(1 for t in self.trades if float(t.get('pnl', 0)) >= 0)
        win_rate = profitable_trades / total_trades if total_trades > 0 else 0.0
        
        pnls = [float(t.get('pnl', 0)) for t in self.trades]
        total_pnl = sum(pnls)
        average_pnl = total_pnl / total_trades if total_trades > 0 else 0.0
        
        max_win = max(pnls) if pnls else 0.0
        max_loss = min(pnls) if pnls else 0.0
        
        # Calculate current streak
        current_streak = 0
        for trade in reversed(self.trades):
            if float(trade.get('pnl', 0)) >= 0:
                current_streak += 1
            else:
                break
        
        return {
            "total_trades": total_trades,
            "win_rate": round(win_rate, 4),
            "total_pnl": round(total_pnl, 2),
            "average_pnl": round(average_pnl, 2),
            "max_win": round(max_win, 2),
            "max_loss": round(max_loss, 2),
            "current_streak": current_streak,
            "best_day": self._get_best_day(),
            "worst_day": self._get_worst_day()
        }

    def _get_best_day(self) -> Optional[str]:
        """Get the best performing day based on PnL."""
        if not self.trades:
            return None
        
        daily_pnl = {}
        for trade in self.trades:
            date = trade.get('timestamp', '')[:10]  # Extract date part
            if date:
                daily_pnl[date] = daily_pnl.get(date, 0) + float(trade.get('pnl', 0))
        
        if daily_pnl:
            best_date = max(daily_pnl.keys(), key=lambda x: daily_pnl[x])
            return f"{best_date}: {daily_pnl[best_date]:.2f}"
        return None

    def _get_worst_day(self) -> Optional[str]:
        """Get the worst performing day based on PnL."""
        if not self.trades:
            return None
        
        daily_pnl = {}
        for trade in self.trades:
            date = trade.get('timestamp', '')[:10]  # Extract date part
            if date:
                daily_pnl[date] = daily_pnl.get(date, 0) + float(trade.get('pnl', 0))
        
        if daily_pnl:
            worst_date = min(daily_pnl.keys(), key=lambda x: daily_pnl[x])
            return f"{worst_date}: {daily_pnl[worst_date]:.2f}"
        return None

    def analyze_trade_statistics(self, trades: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
        """
        Processes a list of trades and writes statistical summary to disk.
        Also returns the computed statistics as a dictionary.

        Args:
            trades (list, optional): List of trade dictionaries, each containing at least 
                                     'pnl' (profit/loss) and 'exit_reason' keys.
                                     If not provided, uses self.trades.

        Returns:
            dict: The computed statistics, or None if no trades.
        """
        trades = trades or self.trades
        logging.debug(f"Starting analysis for {len(trades)} trades.")

        if not trades:
            logging.info("No trades to analyze.")
            return None

        # Initialize statistics
        stats = {
            "total_trades": len(trades),
            "profitable_trades": 0,
            "losing_trades": 0,
            "total_profit": Decimal("0.0"),
            "average_profit_per_trade": 0.0,
            "average_win": 0.0,
            "average_loss": 0.0,
            "max_win": 0.0,
            "max_loss": 0.0,
            "exit_reason_stats": {},
            "timestamp": datetime.utcnow().isoformat()
        }

        wins, losses = [], []

        # Iterate through each trade and compute metrics
        for trade in trades:
            logging.debug(f"Processing trade: {trade}")
            pnl = Decimal(str(trade.get("pnl", 0.0)))
            reason = trade.get("exit_reason", "UNKNOWN")

            if pnl >= 0:
                stats["profitable_trades"] += 1
                wins.append(pnl)
            else:
                stats["losing_trades"] += 1
                losses.append(pnl)

            stats["total_profit"] += pnl

            # Track PnL per exit reason
            if reason not in stats["exit_reason_stats"]:
                stats["exit_reason_stats"][reason] = {"count": 0, "total_pnl": Decimal("0.0")}
            stats["exit_reason_stats"][reason]["count"] += 1
            stats["exit_reason_stats"][reason]["total_pnl"] += pnl

        # Final calculations
        stats["average_profit_per_trade"] = float(stats["total_profit"] / len(trades))
        stats["average_win"] = float(sum(wins) / len(wins)) if wins else 0.0
        stats["average_loss"] = float(sum(losses) / len(losses)) if losses else 0.0
        stats["max_win"] = float(max(wins)) if wins else 0.0
        stats["max_loss"] = float(min(losses)) if losses else 0.0
        stats["win_rate"] = float(stats["profitable_trades"]) / len(trades)

        # Convert Decimal fields to strings for JSON compatibility
        for reason_data in stats["exit_reason_stats"].values():
            reason_data["total_pnl"] = str(reason_data["total_pnl"])
        stats["total_profit"] = str(stats["total_profit"])

        # Load or create the statistics file
        log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs", "live_simulation_trade_statistics.json"))
        try:
            with open(log_path, "r") as f:
                existing_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []

        # Append new stats and sort by timestamp
        existing_data.append(stats)
        existing_data.sort(key=lambda x: x["timestamp"])

        with open(log_path, "w") as f:
            json.dump(existing_data, f, indent=4, ensure_ascii=False)

        logging.debug("Completed trade statistics analysis.")
        logging.info(
            f"Trades analyzed: {len(trades)} | Win rate: {stats['win_rate']:.2%} | "
            f"Avg PnL: {stats['average_profit_per_trade']:.4f} | "
            f"Max Win: {stats['max_win']:.4f} | Max Loss: {stats['max_loss']:.4f} | "
            f"Total PnL: {stats['total_profit']}"
        )

        return stats
