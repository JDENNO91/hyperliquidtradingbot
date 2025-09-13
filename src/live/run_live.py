from application.hyperliquid_sdk.hyperliquid.exchange import Exchange
from application.hyperliquid_sdk.hyperliquid.utils.signing import get_timestamp_ms
from strategy.bbrsi_strategy import BBRSIStrategy
from live.live_risk_manager import RiskManager
from live.live_trade_logger import LiveTradeLogger
from utils import setup_clients  # Ensure utils.py is in same directory
import logging
import time
import sys

 # Reset log file at start
open("logs/live_debug.log", "w").close()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/live_debug.log")
    ]
)
logger = logging.getLogger()

class Live:
    """
    Live handles real-time trading logic using the BBRSI strategy and manages risk on a per-position basis.
    Executes trades using Hyperliquid's SDK and logs all activity.
    """
    def __init__(self):
        _, _, self.config = setup_clients()
        self.logger = logging.getLogger()
        self.logger.info("Live initialised.")

        self.trade_logger = LiveTradeLogger()

        # Load trading configuration
        self.symbol = self.config["trading"]["market"]
        self.interval = self.config["trading"]["timeframe"]
        self.leverage = int(self.config["trading"]["leverage"])
        self.leverage_mode = "isolated"
        self.position_size_pct = float(self.config["trading"]["positionSizePct"])

        # Initialize trading strategy and risk manager
        self.strategy = BBRSIStrategy(logger=self.logger, config=self.config.get("indicators", {}))
        self.risk_manager = RiskManager(logger=self.logger, config=self.config)

        # Setup exchange connection
        self.exchange = Exchange(self.config)  # instantiate exchange client
        self.info = self.exchange.info

        account_info = self.info.user_state(self.exchange.wallet.address)
        account_value = float(account_info["marginSummary"]["accountValue"])
        eth_price = float(self.info.all_mids()[self.symbol])
        self.position_size = (account_value * self.position_size_pct) / eth_price

        self.logger.info(f"Loaded config — Symbol: {self.symbol}, Interval: {self.interval}, Leverage: {self.leverage}, Mode: {self.leverage_mode}, Position Size: {self.position_size:.4f}")

    def cancel_order(self, order_id):
        try:
            response = self.exchange.cancel(self.symbol, order_id)
            self.logger.info(f"Order {order_id} cancelled: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Failed to cancel order {order_id}: {e}")
            return None

    def limit_long(self, symbol, position_size, take_profit):
        try:
            response = self.exchange.order(
                symbol,
                is_buy=True,
                sz=position_size,
                px=take_profit,
                order_type={"limit": {"tif": "GTC"}}
            )
            self.logger.info(f"Limit LONG order placed: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Failed to place limit LONG order: {e}")
            return None

    def limit_short(self, symbol, position_size, take_profit):
        try:
            response = self.exchange.order(
                symbol,
                is_buy=False,
                sz=position_size,
                px=take_profit,
                order_type={"limit": {"tif": "GTC"}}
            )
            self.logger.info(f"Limit SHORT order placed: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Failed to place limit SHORT order: {e}")
            return None


    def run(self):
        consecutive_errors = 0
        MAX_CONSECUTIVE_ERRORS = 5
        # Position size is dynamic based on account balance and configured percentage

        # Set leverage for the trading symbol
        try:
            # Set initial leverage
            self.exchange.update_leverage(self.leverage, self.symbol, is_cross=False)
        except Exception as e:
            self.logger.error(f"Fatal error setting leverage: {e}")
            sys.exit(1)

        interval_minutes = int(self.interval)
        interval_seconds = interval_minutes * 60

        # Main trading loop
        while True:
            try:
                # Fetch latest candle data
                market_data = self.info.candles(self.symbol, self.interval, 50)
                if not market_data or not isinstance(market_data, list) or len(market_data) == 0:
                    raise ValueError("Invalid market data received")

                # Retrieve current open position
                try:
                    open_positions = self.info.user_state(self.exchange.wallet.address)["assetPositions"]
                except Exception as e:
                    self.logger.error(f"Error fetching positions, assuming no open positions: {e}")
                    open_positions = []

                current_position = open_positions[0] if len(open_positions) > 0 else None

                if current_position:
                    self.logger.info(f"Heartbeat — Holding {current_position['position']['szi']} @ {current_position['position']['entryPx']}")
                else:
                    self.logger.info("Heartbeat — No open position.")

                position_size = abs(float(current_position["position"]["szi"])) if current_position else self.position_size

                # Evaluate trading signal
                strategy_result = self.strategy.evaluate_position(market_data)

                # Check if a valid signal was returned
                if not strategy_result or not hasattr(strategy_result, "signal"):
                    self.logger.warning("No valid signal returned from strategy.")
                    time.sleep(interval_seconds)
                    continue

                # Evaluate risk management action based on position drawdown
                if current_position:
                    action_result = self.risk_manager.evaluate_position_drawdown(current_position)
                    if action_result and action_result["action"] == "reduce":
                        self.logger.warning(f"Drawdown action: {action_result['reason']}, reducing size by factor {action_result['adjustment']}")
                        self.position_size *= action_result["adjustment"]

                # Execute trade based on strategy signal and current position status
                if strategy_result.signal == "LONG" and not current_position:
                    self.logger.info("Opening long position (market order)")
                    self.logger.info(f"Signal=LONG, RSI={strategy_result.indicators.get('rsi')}, ADX={strategy_result.indicators.get('adx')}")
                    self.exchange.market_open(self.symbol, is_buy=True, sz=position_size)
                    trade = {
                        "type": "OPEN_LONG",
                        "symbol": self.symbol,
                        "size": position_size,
                        "timestamp": get_timestamp_ms(),
                        "indicators": strategy_result.indicators
                    }
                    self.trade_logger.log_trade(trade)
                elif strategy_result.signal == "SHORT" and not current_position:
                    self.logger.info("Opening short position (market order)")
                    self.logger.info(f"Signal=SHORT, RSI={strategy_result.indicators.get('rsi')}, ADX={strategy_result.indicators.get('adx')}")
                    self.exchange.market_open(self.symbol, is_buy=False, sz=position_size)
                    trade = {
                        "type": "OPEN_SHORT",
                        "symbol": self.symbol,
                        "size": position_size,
                        "timestamp": get_timestamp_ms(),
                        "indicators": strategy_result.indicators
                    }
                    self.trade_logger.log_trade(trade)
                elif strategy_result.signal == "CLOSE_LONG" and current_position and float(current_position["position"]["szi"]) > 0:
                    entry_price = float(current_position["position"]["entryPx"])
                    exit_price = float(self.info.all_mids()[self.symbol])
                    size = abs(float(current_position["position"]["szi"]))
                    pnl = (exit_price - entry_price) * size

                    self.logger.info(f"Closing LONG — Entry: {entry_price}, Exit: {exit_price}, PnL: {pnl:.2f}")

                    trade = {
                        "type": "CLOSE_LONG",
                        "symbol": self.symbol,
                        "size": size,
                        "entry": entry_price,
                        "exit": exit_price,
                        "pnl": pnl,
                        "timestamp": get_timestamp_ms(),
                        "reason": f"RSI={strategy_result.indicators.get('rsi')}, ADX={strategy_result.indicators.get('adx')}"
                    }
                    self.trade_logger.log_trade(trade)
                elif strategy_result.signal == "CLOSE_SHORT" and current_position and float(current_position["position"]["szi"]) < 0:
                    entry_price = float(current_position["position"]["entryPx"])
                    exit_price = float(self.info.all_mids()[self.symbol])
                    size = abs(float(current_position["position"]["szi"]))
                    pnl = (entry_price - exit_price) * size

                    self.logger.info(f"Closing SHORT — Entry: {entry_price}, Exit: {exit_price}, PnL: {pnl:.2f}")

                    trade = {
                        "type": "CLOSE_SHORT",
                        "symbol": self.symbol,
                        "size": size,
                        "entry": entry_price,
                        "exit": exit_price,
                        "pnl": pnl,
                        "timestamp": get_timestamp_ms(),
                        "reason": f"RSI={strategy_result.indicators.get('rsi')}, ADX={strategy_result.indicators.get('adx')}"
                    }
                    self.trade_logger.log_trade(trade)

                # Position size reduction due to strategy is now handled via the risk manager.

                # Handle consecutive error tracking
                consecutive_errors = 0

            except Exception as e:
                consecutive_errors += 1
                self.logger.error(f"Error executing trade ({consecutive_errors}/{MAX_CONSECUTIVE_ERRORS}): {e}")

                if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                    self.logger.error("Too many consecutive errors, stopping bot")
                    sys.exit(1)

            time.sleep(interval_seconds)


def save_trade_statistics():
    import json
    from pathlib import Path

    trade_file = Path("logs/live_trades.json")
    stats_file = Path("live_trade_statistics.json")

    if not trade_file.exists():
        return

    with open(trade_file, "r") as f:
        trades = json.load(f)

    total = len(trades)
    wins = sum(1 for t in trades if t.get("pnl", 0) > 0)
    losses = sum(1 for t in trades if t.get("pnl", 0) < 0)
    avg_pnl = sum(t.get("pnl", 0) for t in trades) / total if total > 0 else 0
    stats = {
        "totalTrades": total,
        "profitableTrades": wins,
        "losingTrades": losses,
        "winRate": f"{(wins / total) * 100:.2f}%" if total > 0 else "0.00%",
        "averageProfitPerTrade": avg_pnl,
    }

    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=2)


def main():
    # Main entrypoint: sets up client and starts live trading
    # logging.basicConfig(level=logging.INFO)
    address, info, exchange = setup_clients()
    trader = Live()
    trader.exchange = exchange
    try:
        trader.run()
    finally:
        save_trade_statistics()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        save_trade_statistics()
        sys.exit(1)
