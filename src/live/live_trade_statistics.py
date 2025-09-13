import os
import json
import logging
from datetime import datetime

def analyze_trade_statistics(self):
    """Analyzes live trades and writes statistics to live_trade_statistics.json"""
    trades = getattr(self, "trades", [])
    if not trades:
        logging.info("No trades to analyze.")
        return

    stats = {
        "total_trades": len(trades),
        "profitable_trades": 0,
        "losing_trades": 0,
        "total_profit": 0.0,
        "average_profit_per_trade": 0.0,
        "average_win": 0.0,
        "average_loss": 0.0,
        "max_win": float("-inf"),
        "max_loss": float("inf"),
        "exit_reason_stats": {},
        "timestamp": datetime.utcnow().isoformat()
    }

    wins = []
    losses = []

    for trade in trades:
        profit = trade.get("pnl", 0.0)
        reason = trade.get("exit_reason", "UNKNOWN")

        if profit >= 0:
            stats["profitable_trades"] += 1
            wins.append(profit)
            if profit > stats["max_win"]:
                stats["max_win"] = profit
        else:
            stats["losing_trades"] += 1
            losses.append(profit)
            if profit < stats["max_loss"]:
                stats["max_loss"] = profit

        stats["total_profit"] += profit
        stats["exit_reason_stats"].setdefault(reason, {"count": 0, "total_pnl": 0.0})
        stats["exit_reason_stats"][reason]["count"] += 1
        stats["exit_reason_stats"][reason]["total_pnl"] += profit

    stats["average_profit_per_trade"] = stats["total_profit"] / len(trades)
    stats["average_win"] = sum(wins) / len(wins) if wins else 0.0
    stats["average_loss"] = sum(losses) / len(losses) if losses else 0.0

    log_path = os.path.join(os.path.dirname(__file__), "..", "logs", "live_trade_statistics.json")
    log_path = os.path.abspath(log_path)
    with open(log_path, "w") as f:
        json.dump([stats], f, indent=4)

    logging.info("Live trade statistics written to live_trade_statistics.json")
