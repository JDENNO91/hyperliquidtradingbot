import json
import os
from datetime import datetime


TRADE_LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs", "live_trades.json"))
CSV_LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs", "live_trades.csv"))

# Ensure the log file exists before class definition
if not os.path.exists(TRADE_LOG_PATH):
    with open(TRADE_LOG_PATH, "w") as f:
        json.dump([], f)

# Clear the log file on each new run
with open(TRADE_LOG_PATH, "w") as f:
    json.dump([], f)

class LiveTradeLogger:
    def __init__(self, log_path=TRADE_LOG_PATH):
        self.log_path = log_path

    def log_trade(self, market, side, entry_price, exit_price, size, pnl, drawdown, exit_reason, simulated_balance, verbose=False):
        trade_data = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "market": market,
            "side": f"Simulated {side}",
            "entry_price": entry_price,
            "exit_price": exit_price,
            "size": size,
            "pnl": pnl,
            "drawdown": drawdown,
            "exit_reason": exit_reason,
            "simulated_balance": simulated_balance
        }

        if not os.path.exists(self.log_path):
            with open(self.log_path, "w") as f:
                json.dump([], f)

        try:
            with open(self.log_path, "r") as f:
                trades = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            trades = []

        trades.append(trade_data)

        with open(self.log_path, "w") as f:
            json.dump(trades, f, indent=4)

        import csv
        write_header = not os.path.exists(CSV_LOG_PATH) or os.path.getsize(CSV_LOG_PATH) == 0
        with open(CSV_LOG_PATH, mode="a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=trade_data.keys())
            if write_header:
                writer.writeheader()
            writer.writerow(trade_data)

        if verbose:
            print(f"Logged simulated trade: {trade_data}")

    def get_all_trades(self):
        try:
            with open(self.log_path, "r") as f:
                return json.load(f)
        except Exception:
            return []