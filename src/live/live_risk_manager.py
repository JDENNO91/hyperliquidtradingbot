import threading
import time

class RiskManager:
    def __init__(self, config, logger, exchange, address=None, info=None, threshold=0.10, poll_interval=5):
        self.config = config
        self.logger = logger
        self.exchange = exchange
        self.address = address
        self.info = info
        self.threshold = threshold
        self.poll_interval = poll_interval
        self._stopped = False
        self.high_water_mark = 0.0
        self._lock = threading.Lock()
        if self.info and self.address:
            self.high_water_mark = self.get_account_value()

        self.logger.info(f"Initial account value: {self.high_water_mark:.4f}")
        self._drawdown_triggered = False
        self.poller = threading.Thread(target=self._poll_loop, daemon=True)
        self.poller.start()

    def get_account_value(self):
        if not self.info or not self.address:
            self.logger.warning("Info or address not provided, returning 0 as account value.")
            return 0.0
        try:
            state = self.info.user_state(self.address)
        except Exception as e:
            self.logger.error(f"Failed to fetch user state: {e}")
            return 0.0
        total = 0.0

        for bal in state.get("balances", []):
            total += float(bal.get("amount", 0))

        positions = state.get("assetPositions", [])
        for pos in positions:
            size = float(pos["position"]["szi"])
            if size == 0:
                continue
            coin = pos["position"]["coin"]
            book = self.info.l2_book(coin)
            bid = float(book["data"]["levels"][0][0]["px"])
            ask = float(book["data"]["levels"][1][0]["px"])
            mid = (bid + ask) / 2
            total += size * mid

        return round(total, 2)

    def _poll_loop(self):
        while not self._stopped:
            current = self.get_account_value()

            if self.high_water_mark == 0 and current == 0:
                self.logger.info("No positions open, skipping drawdown check.")
                self.logger.warning("Account value and high water mark are both 0 — skipping drawdown check.")
                time.sleep(self.poll_interval)
                continue

            if current > self.high_water_mark:
                with self._lock:
                    self.high_water_mark = current

            drawdown = (self.high_water_mark - current) / self.high_water_mark
            self.logger.info(f"Value={current:.4f}, Peak={self.high_water_mark:.4f}, Drawdown={drawdown*100:.2f}%")

            if drawdown >= self.threshold:
                self.logger.warning(f"Drawdown {drawdown*100:.2f}% >= {self.threshold*100:.1f}% — closing all positions.")
                self.close_all_positions()
                self._drawdown_triggered = True
                self.logger.warning("Drawdown protection triggered — monitoring stopped.")
                break

            time.sleep(self.poll_interval)

    def close_all_positions(self):
        if not self.info or not self.address:
            self.logger.warning("Info or address not provided, cannot close positions.")
            return
        state = self.info.user_state(self.address)
        for pos in state.get("assetPositions", []):
            size = float(pos["position"]["szi"])
            coin = pos["position"]["coin"]
            if size == 0:
                continue

            close_size = abs(size)
            try:
                resp = self.exchange.market_close(coin, sz=abs(size))
                if resp.get("status") == "ok":
                    self.logger.info(f"Closed {close_size} {coin} via market close.")
                else:
                    self.logger.error(f"Failed to close {coin} ({close_size}): {resp}")
            except Exception as e:
                self.logger.error(f"Exception while closing {coin}: {e}")

    def drawdown_triggered(self):
        self.logger.debug(f"drawdown_triggered() called — returning {self._drawdown_triggered}")
        return self._drawdown_triggered

    def stop(self):
        self._stopped = True
        if self.poller.is_alive():
            self.poller.join()