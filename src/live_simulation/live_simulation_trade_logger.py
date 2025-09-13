import json
import os
from datetime import datetime
import pytz
import uuid
import csv
import logging

def get_livesim_logger(log_path):
    logger = logging.getLogger("LiveSimLogger")
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        file_handler = logging.FileHandler(log_path, mode='a')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    return logger

logger = logging.getLogger("LiveSimLogger")

LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs", "live_simulation_debug.log"))

# Prevent duplicate handlers
if logger.hasHandlers():
    logger.handlers.clear()

# File handler for debug log (captures everything)
file_handler = logging.FileHandler(LOG_PATH, mode='a')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(file_handler)

# Console handler (optional: can be set to WARNING or higher to reduce terminal spam)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)  # Only show warnings/errors in terminal
console_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(console_handler)

TRADE_LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs", "live_simulation_trades.json"))
CSV_LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs", "live_simulation_trades.csv"))

# Only clear the log file at startup, not on every import
if os.environ.get("LIVESIM_CLEAR_LOGS", "1") == "1":
    with open(TRADE_LOG_PATH, "w") as f:
        json.dump([], f)
    # Also clear CSV if desired
    with open(CSV_LOG_PATH, "w") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp", "trade_id", "market", "side", "entry_price", "exit_price",
            "entry_time", "exit_time", "size", "pnl", "drawdown", "exit_reason", "simulated_balance"
        ])
    # Prevent clearing logs on subsequent imports in the same process
    os.environ["LIVESIM_CLEAR_LOGS"] = "0"

class LiveSimulationTradeLogger:
    def __init__(self, log_path=TRADE_LOG_PATH, csv_log_path=None):
        """
        Initialize the trade logger with paths for JSON and CSV logs.
        CSV path is always set to the static CSV_LOG_PATH.
        """
        self.log_path = log_path
        self.csv_log_path = CSV_LOG_PATH

    def heartbeat(self):
        """
        Log a heartbeat message indicating the logger is active.
        """
        logger.debug(f"LiveSimulationTradeLogger heartbeat: logger is active and path is {self.csv_log_path}")

    def get_all_trades(self):
        """
        Retrieve all logged trades from the JSON log file.
        Returns an empty list if the file is missing or unreadable.
        """
        try:
            with open(self.log_path, "r") as f:
                return json.load(f)
        except Exception:
            logger.exception("Failed to read trade log JSON file")
            return []

    def log_trade(self, market, side, entry_price, exit_price, size, pnl, drawdown, exit_reason,
                  simulated_balance, entry_time, exit_time, verbose=False):
        logger.debug(f"Attempting to log trade: market={market}, side={side}, entry_price={entry_price}, "
                     f"exit_price={exit_price}, size={size}, pnl={pnl}, drawdown={drawdown}, "
                     f"exit_reason={exit_reason}, simulated_balance={simulated_balance}, "
                     f"entry_time={entry_time}, exit_time={exit_time}")

        if not side or side.upper() not in ("LONG", "SHORT"):
            logger.warning(f"Attempted to log trade with invalid or missing side: {side}. Skipping log.")
            return

        # Validate required trade data at the top
        critical_fields = {
            "market": market,
            "side": side,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "size": size,
            "pnl": pnl,
            "simulated_balance": simulated_balance,
            "entry_time": entry_time,
            "exit_time": exit_time
        }
        missing_fields = [k for k, v in critical_fields.items() if v is None]
        if missing_fields:
            logger.warning(f"Trade log skipped — missing fields: {', '.join(missing_fields)} | Trade details: {critical_fields}")
            return

        # Ensure JSON log file exists and is initialized
        if not os.path.exists(self.log_path):
            logger.debug(f"Trade log file {self.log_path} does not exist. Creating new file.")
            with open(self.log_path, "w") as f:
                json.dump([], f)

        # Calculate updated simulated balance for the trade
        account = simulated_balance
        trade_data = {
            "timestamp": datetime.now(pytz.timezone("Europe/London")).strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
            "trade_id": str(uuid.uuid4()),
            "market": market,
            "side": f"Simulated {side}",
            "entry_price": entry_price,
            "exit_price": exit_price,
            "entry_time": entry_time,
            "exit_time": exit_time,
            "size": size,
            "pnl": pnl,
            "drawdown": None if drawdown is None else round(drawdown, 2),
            "exit_reason": exit_reason,
            "simulated_balance": round(account, 2)
        }
        logger.debug(f"Prepared trade data for logging: {trade_data}")

        # Load existing trades and append new trade
        try:
            with open(self.log_path, "r") as f:
                trades = json.load(f)
            logger.debug(f"Loaded {len(trades)} existing trades from JSON log.")
        except (FileNotFoundError, json.JSONDecodeError):
            trades = []
            logger.warning("Trade log file missing or corrupt, starting new log.")

        trades.append(trade_data)

        # Write updated trades list back to JSON log file
        try:
            with open(self.log_path, "w") as f:
                json.dump(trades, f, indent=4)
            logger.debug(f"Appended trade to JSON log. Total trades now: {len(trades)}")
        except Exception:
            logger.exception("Failed to write trade to JSON log")
            return

        # Format entry and exit times for CSV output
        try:
            formatted_entry_time = datetime.fromtimestamp(entry_time).strftime("%H:%M:%S")
        except (OSError, TypeError, ValueError):
            formatted_entry_time = "INVALID"

        try:
            formatted_exit_time = datetime.fromtimestamp(exit_time).strftime("%H:%M:%S")
        except (OSError, TypeError, ValueError):
            formatted_exit_time = "INVALID"

        # Determine if CSV header needs to be written
        write_header = not os.path.exists(self.csv_log_path) or os.path.getsize(self.csv_log_path) == 0

        # Write trade data to CSV log
        try:
            with open(self.csv_log_path, "a", newline="") as f:
                writer = csv.writer(f)
                if write_header:
                    logger.debug("CSV log does not exist or is empty. Writing header row.")
                    writer.writerow([
                        "timestamp", "trade_id", "market", "side", "entry_price", "exit_price",
                        "entry_time", "exit_time", "size", "pnl", "drawdown", "exit_reason", "simulated_balance"
                    ])
                writer.writerow([
                    trade_data["timestamp"],
                    trade_data["trade_id"],
                    trade_data["market"],
                    trade_data["side"],
                    f"{float(trade_data['entry_price']):.2f}",
                    f"{float(trade_data['exit_price']):.2f}",
                    formatted_entry_time,
                    formatted_exit_time,
                    f"{float(trade_data['size']):.6f}",
                    f"{float(trade_data['pnl']):.2f}",
                    f"{trade_data['drawdown'] if trade_data['drawdown'] is not None else '0.00'}",
                    trade_data["exit_reason"],
                    trade_data["simulated_balance"]
                ])
                f.flush()
            logger.debug("Trade successfully written to CSV log.")
        except Exception:
            logger.exception("Failed to write to CSV log")

        # Always log trade details to debug log (not terminal)
        logger.debug(f"Logged simulated trade: {trade_data}")
        logger.info(f"Trade logged: {trade_data}")

        # Optionally, flush all handlers to ensure logs are written immediately
        for handler in logger.handlers:
            handler.flush()