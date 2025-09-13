"""
Live Simulation CLI

This module provides a unified command-line interface for live simulation (paper trading),
allowing users to test strategies with live market data without executing real trades.
"""

import argparse
import sys
import logging
import asyncio
import time
import os
from pathlib import Path
from typing import Optional, Dict, Any

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config.config_manager import ConfigManager
from src.application.hyperliquid_sdk.hyperliquid.info import Info
from src.application.hyperliquid_sdk.hyperliquid.exchange import Exchange
from src.strategies.core.bbrsi_strategy import BBRSIStrategy
from src.strategies.core.scalping_strategy import ScalpingStrategy
from src.live_simulation.simple_risk_manager import SimpleRiskManager
from src.live_simulation.live_simulation_trade_logger import LiveSimulationTradeLogger, get_livesim_logger
from src.live_simulation.utils import setup_clients
from src.live_simulation.live_simulation_trade_statistics import LiveSimulationTradeStatistics

def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """Set up logging configuration."""
    logger = logging.getLogger("simulate")
    logger.setLevel(getattr(logging, level.upper()))
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

class LiveSimulationCLI:
    """
    Handles simulated trading logic using a strategy and manages simulated positions,
    PnL, and risk, while logging all activity. No real orders are placed; all actions are simulated.
    """

    def __init__(self, exchange: Exchange, config: dict, info: Info, trades: list = None):
        # --- Simulation State ---
        self.trades = trades or []
        self.logger = logging.getLogger("simulate")
        self.logger.info("LiveSimulation initialised in test mode — no live trades will be executed.")
        self.trade_logger = LiveSimulationTradeLogger()  # Handles trade logging to file/CSV
        self.config = config
        self.symbol = self.config["trading"]["market"].replace("-PERP", "")
        self.interval = self.config["trading"]["timeframe"]
        self.leverage = int(self.config["trading"]["leverage"])
        self.leverage_mode = "isolated"
        self.position_size_pct = float(self.config["trading"]["positionSizePct"])
        self.slippage = float(self.config["trading"].get("slippage", 0.0))
        self.stop_loss_pct = float(self.config["trading"].get("stopLoss", 0.0))

        # --- Account Setup ---
        simulated_starting_balance = float(self.config["trading"].get("initial_capital", 10000.0))
        self.account_value = simulated_starting_balance
        self.peak_value = simulated_starting_balance

        # --- Strategy Selection ---
        strategy_name = self.config.get("strategy", "bbrsi").lower()
        if strategy_name == "bbrsi":
            self.strategy = BBRSIStrategy(config=self.config, logger=self.logger)
        elif strategy_name == "scalping":
            self.strategy = ScalpingStrategy(config=self.config, logger=self.logger)
        else:
            self.logger.warning(f"Unknown strategy '{strategy_name}', defaulting to BBRSI")
            self.strategy = BBRSIStrategy(config=self.config, logger=self.logger)

        # --- Risk Manager and Exchange Info ---
        # Use simple risk manager for simulation
        self.risk_manager = SimpleRiskManager(
            initial_balance=simulated_starting_balance,
            max_drawdown=0.25
        )
        self.exchange = exchange
        self.info = info

        # --- Position Sizing ---
        # Calculate initial position size based on simulated balance and latest market price
        end = int(time.time() * 1000)
        start = end - 5 * 60 * 1000
        market_data = self.info.candles_snapshot(self.symbol, self.interval, start, end)
        eth_price = float(market_data[-1]["c"]) if market_data else 1.0
        self.position_size = (simulated_starting_balance * self.position_size_pct) / eth_price

        # --- Position State ---
        self.simulated_position = {"side": None, "size": 0}
        self.last_closed_position = None
        self.position_open_time = None
        self.no_signal_counter = 0
        self.last_drawdown = None

        # --- Log Initial State ---
        self.logger.info(f"symbol {self.symbol}")
        self.logger.info(f"interval {self.interval}")
        self.logger.info(f"leverage {self.leverage}")
        self.logger.info(f"leverage_mode {self.leverage_mode}")
        self.logger.info(f"position_size {self.position_size}")

    # --- Utility Methods ---
    def calculate_pnl(self, entry_price, exit_price, size, side):
        """Calculate profit and loss for a closed position."""
        if side == "LONG":
            return round((exit_price - entry_price) * size, 2)
        elif side == "SHORT":
            return round((entry_price - exit_price) * size, 2)
        return 0.0

    def get_latest_price(self, symbol, retries=3, delay=2):
        """Fetch the latest price for a symbol, with retries for robustness."""
        for _ in range(retries):
            try:
                return float(self.exchange.info.all_mids()[symbol])
            except Exception as e:
                self.logger.warning(f"Retrying fetch for all_mids due to: {e}")
                time.sleep(delay)
        self.logger.error(f"Failed to fetch all_mids after {retries} attempts.")
        return None

    # --- Market Interface Methods ---
    def market_open(self, symbol, is_buy, sz):
        """Simulate opening a position (LONG or SHORT) with slippage and update account state."""
        if self.simulated_position["side"]:
            self.logger.warning("Attempted to open a position while one is already open. Ignoring.")
            return
        side = "LONG" if is_buy else "SHORT"
        self.logger.info(f"Simulated opening {side} position of size {sz} on {symbol} with slippage={self.slippage}")
        self.logger.debug(f"market_open called: symbol={symbol}, side={side}, size={sz}, slippage={self.slippage}")
        self.simulated_position = {"side": side, "size": sz}
        raw_price = self.get_latest_price(self.symbol)
        if raw_price is None:
            self.logger.error("Failed to fetch all_mids in market_open after 3 attempts.")
            return
        entry_price = raw_price * (1 + self.slippage) if is_buy else raw_price * (1 - self.slippage)
        self.account_value -= sz * raw_price
        self.simulated_position["entry_price"] = entry_price
        self.logger.info(f"Entry price for {side} position: {entry_price:.2f}")
        self.logger.info(f"Account value after entry: {self.account_value:.2f}")
        # Update risk manager
        self.risk_manager.update_balance(self.account_value)
        self.logger.debug(f"Position state after open: {self.simulated_position}")
        self.position_open_time = time.time()

    def market_close(self, symbol):
        """Simulate closing the current position and update account state (no trade logging here)."""
        if not self.simulated_position["side"]:
            self.logger.info(f"No simulated position to close on {symbol}")
            self.logger.debug("market_close called but no position was open.")
            return
        side = self.simulated_position["side"]
        size = self.simulated_position["size"]
        entry_price = self.simulated_position.get("entry_price", 0.0)
        raw_exit_price = self.get_latest_price(self.symbol)
        if raw_exit_price is None:
            self.logger.error("Failed to fetch all_mids in market_close after 3 attempts.")
            return
        exit_price = raw_exit_price * (1 - self.slippage) if side == "LONG" else raw_exit_price * (1 + self.slippage)
        fee_rate = 0.0007  # Taker fee
        gross_pnl = self.calculate_pnl(entry_price, exit_price, size, side)
        fees = fee_rate * (entry_price + exit_price) * size
        pnl = round(gross_pnl - fees, 2)
        self.account_value += exit_price * size
        self.account_value += pnl
        if self.account_value > self.peak_value:
            self.peak_value = self.account_value
        eth_price = self.get_latest_price(self.symbol)
        if eth_price is None:
            self.logger.error("Failed to fetch all_mids in market_close for position size update after 3 attempts.")
            eth_price = 1.0
        self.position_size = (self.account_value * self.position_size_pct) / eth_price
        drawdown = 100.0 * (self.peak_value - self.account_value) / self.peak_value
        # Update risk manager
        self.risk_manager.update_balance(self.account_value)

        self.logger.debug(
            f"market_close called: symbol={symbol}, side={side}, size={size}, entry_price={entry_price}, "
            f"exit_price={exit_price}, pnl={pnl}, drawdown={drawdown}, account_value={self.account_value}"
        )

        # DO NOT log the trade here!
        # Only update state
        self.logger.info(f"Simulated closing {side} position on {symbol}")
        self.logger.info(f"Entry: {entry_price:.2f}, Exit: {exit_price:.2f}, Size: {size:.6f}")
        self.logger.info(f"PnL: {pnl:.2f}, Updated Account Value: {self.account_value:.2f}")
        self.logger.info(f"Closed {side} position: Entry={entry_price:.2f}, Exit={exit_price:.2f}, PnL={pnl:.2f}, New Balance={self.account_value:.2f}")
        self.logger.debug(f"Position state after close: {self.simulated_position}")
        self.last_closed_position = self.simulated_position.copy()
        self.simulated_position = {"side": None, "size": 0}
        self.last_drawdown = drawdown
        self.position_open_time = None

    # --- Monitoring Methods ---
    def update_position_metrics(self):
        """Update and log current position metrics."""
        if not self.simulated_position["side"]:
            return
        current_price = self.get_latest_price(self.symbol)
        if current_price is None:
            return
        entry_price = self.simulated_position.get("entry_price", 0)
        if entry_price == 0:
            return
        size = self.simulated_position["size"]
        side = self.simulated_position["side"]
        unrealized_pnl = self.calculate_pnl(entry_price, current_price, size, side)
        unrealized_pnl_pct = (unrealized_pnl / (entry_price * size)) * 100
        self.logger.debug(f"Unrealized PnL: {unrealized_pnl:.2f} ({unrealized_pnl_pct:.2f}%)")

    def handle_strategy_signal(self, strategy_result):
        """Handle strategy signals and execute simulated trades."""
        if not strategy_result:
            self.no_signal_counter += 1
            if self.no_signal_counter % 10 == 0:
                self.logger.debug(f"No signal for {self.no_signal_counter} consecutive ticks")
            return

        # Handle both dictionary and Signal object inputs
        if hasattr(strategy_result, 'direction'):
            # Signal object
            signal_type = strategy_result.direction
            signal_reason = strategy_result.reason
        else:
            # Dictionary
            signal_type = strategy_result.get("signal")
            signal_reason = strategy_result.get("reason")
            
        if not signal_type:
            return

        self.logger.info(f"Strategy signal: {signal_type}")
        
        if signal_type == "LONG" and not self.simulated_position["side"]:
            self.market_open(self.symbol, True, self.position_size)
        elif signal_type == "SHORT" and not self.simulated_position["side"]:
            self.market_open(self.symbol, False, self.position_size)
        elif signal_type in ["CLOSE_LONG", "CLOSE_SHORT", "CLOSE_ALL"] and self.simulated_position["side"]:
            self.market_close(self.symbol)
            self.process_trade_closure(signal_type, strategy_result)

    def process_trade_closure(self, signal, strategy_result):
        """Log and record trade closure details after a simulated position is closed."""
        last_pos = self.last_closed_position or {}
        if not last_pos.get("side"):
            self.logger.warning("No closed position to log. Skipping trade log.")
            return
        entry_price = last_pos.get("entry_price")
        size = last_pos.get("size")
        side = last_pos.get("side")
        self.logger.debug(f"Trade closure data — entry: {entry_price}, exit: {self.get_latest_price(self.symbol)}, size: {size}, side: {side}")
        exit_price = self.get_latest_price(self.symbol) or entry_price
        if None in (entry_price, exit_price, size, side):
            self.logger.error("Trade data contains None values. Skipping trade log.")
            return
        pnl = self.calculate_pnl(entry_price, exit_price, size, side)
        # Handle both dictionary and Signal object inputs for exit reason
        if hasattr(strategy_result, 'reason'):
            # Signal object
            exit_reason = strategy_result.reason or f"{side} CLOSED"
        else:
            # Dictionary
            exit_reason = strategy_result.get("reason") or strategy_result.get("exit_reason") or f"{side} CLOSED"
        drawdown = getattr(self, "last_drawdown", None)
        entry_time = self.position_open_time or time.time()
        # Use trade logger for all trade logging
        self.trade_logger.log_trade(
            market=self.symbol,
            side=side,
            entry_price=entry_price,
            exit_price=exit_price,
            size=size,
            pnl=pnl,
            drawdown=drawdown,
            exit_reason=exit_reason,
            simulated_balance=self.account_value,
            entry_time=entry_time,
            exit_time=time.time()
        )

    # --- Main Simulation Loop ---
    async def run(self, duration_hours: int = 24, max_trades: Optional[int] = None):
        """
        Main simulation loop:
        - Fetches market data
        - Evaluates strategy
        - Handles signals and updates metrics
        - Runs for specified duration or until stopped
        """
        consecutive_errors = 0
        MAX_CONSECUTIVE_ERRORS = 5
        trade_count = 0
        
        try:
            self.logger.info("Simulated mode: using internal account balance.")
            self.logger.info(f"Trading {self.symbol} on timeframe {self.interval} with {self.leverage}x leverage (isolated)")
            self.logger.info("Skipping leverage update — simulation mode does not require exchange calls.")
        except Exception as e:
            self.logger.error(f"Fatal error setting leverage: {e}")
            sys.exit(1)
            
        interval_minutes = int("".join(filter(str.isdigit, self.interval)))
        interval_seconds = interval_minutes * 60
        last_stats_save = time.time()
        stats_interval = 300  # Save stats every 5 minutes
        end_time = time.time() + (duration_hours * 3600)  # Convert hours to seconds
        
        self.logger.info(f"Starting simulation for {duration_hours} hours (until {time.ctime(end_time)})")
        if max_trades:
            self.logger.info(f"Maximum trades limit: {max_trades}")
        
        while time.time() < end_time:
            loop_start_time = time.time()
            
            # Check trade limit
            if max_trades and trade_count >= max_trades:
                self.logger.info(f"Reached maximum trade limit ({max_trades}), stopping simulation")
                break
                
            try:
                now = int(time.time() * 1000)
                
                # Heartbeat log every minute
                if int(time.time()) % 60 == 0:
                    try:
                        earlier_hb = now - 50 * interval_seconds * 1000
                        market_data_hb = self.info.candles_snapshot(self.symbol, self.interval, earlier_hb, now)
                        if market_data_hb and isinstance(market_data_hb, list) and len(market_data_hb) > 0:
                            self.logger.info(f"Heartbeat — bot is running. Last close price: {market_data_hb[-1]['c']}")
                        else:
                            self.logger.info("Heartbeat — bot is running. No market data available for last close price.")
                    except Exception:
                        self.logger.info("Heartbeat — bot is running. (Could not fetch last close price)")
                
                # Fetch latest market data for strategy evaluation
                earlier = now - 50 * interval_seconds * 1000
                for _ in range(3):
                    try:
                        market_data = self.info.candles_snapshot(self.symbol, self.interval, earlier, now)
                        break
                    except Exception as e:
                        self.logger.warning(f"Retrying fetch due to: {e}")
                        time.sleep(2)
                else:
                    self.logger.error("Failed to fetch market data after 3 attempts.")
                    continue
                    
                if not market_data or not isinstance(market_data, list) or len(market_data) == 0:
                    raise ValueError("Invalid market data received")
                    
                self.logger.info(f"Latest candle (close): {market_data[-1]['c']}")
                self.logger.debug(f"Market data sample (last 2): {market_data[-2:]}")
                self.logger.info(f"Market data length: {len(market_data)}")
                
                if len(market_data) < 50:
                    self.logger.warning("Insufficient candles for indicator calculation — skipping this tick.")
                    await asyncio.sleep(interval_seconds)
                    continue
                    
                # Convert OHLCV fields to float for indicator calculations
                for candle in market_data:
                    candle["c"] = float(candle["c"])
                    candle["h"] = float(candle["h"])
                    candle["l"] = float(candle["l"])
                    
                self.logger.debug(f"Passing {len(market_data)} candles to strategy.")
                self.logger.debug("Calling strategy.evaluate_position with market data...")
                
                # Evaluate current position for exit signals
                if self.simulated_position["side"]:
                    strategy_result = await self.strategy.evaluate_position(market_data, len(market_data) - 1)
                    self.logger.debug(f"Strategy returned: {strategy_result}")
                    
                    # Cooldown logic: skip signal if just closed a position
                    if (
                        self.last_closed_position
                        and self.position_open_time
                        and (time.time() - self.position_open_time < 2 * interval_seconds)
                    ):
                        self.logger.info("Cooldown active — skipping signal.")
                        await asyncio.sleep(interval_seconds)
                        continue
                        
                    # Only process non-NONE signals
                    if strategy_result and strategy_result.direction != "NONE":
                        self.handle_strategy_signal(strategy_result)
                        
                        # Count trades
                        signal_type = strategy_result.direction if hasattr(strategy_result, 'direction') else strategy_result.get("signal")
                        if signal_type in ["CLOSE_LONG", "CLOSE_SHORT", "CLOSE_ALL"]:
                            trade_count += 1
                            self.logger.info(f"Trade #{trade_count} completed")
                
                # Generate entry signals if no position is open
                if not self.simulated_position["side"]:
                    strategy_result = await self.strategy.generate_signal(market_data, len(market_data) - 1)
                    if strategy_result and strategy_result.direction in ["LONG", "SHORT"]:
                        self.handle_strategy_signal({"signal": strategy_result.direction})
                
                # Save trade statistics periodically
                if time.time() - last_stats_save >= stats_interval:
                    self.save_trade_statistics()
                    last_stats_save = time.time()
                    
                self.update_position_metrics()
                self.logger.debug(f"Loop duration: {time.time() - loop_start_time:.2f}s")
                
                await asyncio.sleep(interval_seconds)
                continue
                
            except Exception as e:
                consecutive_errors += 1
                if self.simulated_position["side"] not in ("LONG", "SHORT", None):
                    self.logger.warning(f"Unexpected simulated position state: {self.simulated_position['side']}")
                self.logger.error(f"Error executing simulated trade ({consecutive_errors}/{MAX_CONSECUTIVE_ERRORS}): {e}")
                
                if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                    self.logger.error("Too many consecutive errors, stopping bot")
                    sys.exit(1)
                    
        self.logger.info(f"Simulation completed. Total trades: {trade_count}")
        self.save_trade_statistics()

    def save_trade_statistics(self):
        """Save trade statistics to file."""
        try:
            stats_analyzer = LiveSimulationTradeStatistics()
            stats = stats_analyzer.get_current_performance_summary()
            self.logger.info(f"Trade Stats — Total: {stats['total_trades']}, Win Rate: {stats['win_rate']:.2%}, "
                           f"Total PnL: ${stats['total_pnl']:.2f}, Avg PnL: ${stats['average_pnl']:.2f}")
        except Exception as e:
            self.logger.error(f"Failed to save trade statistics: {e}")

def simulate_cli():
    """Main simulation CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Hyperliquid Trading Bot - Live Simulation Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start simulation with default ETH configuration
  python -m src.cli.simulate --profile live_eth
  
  # Simulation with custom parameters
  python -m src.cli.simulate --profile live_btc --timeframe 15m --leverage 10
  
  # Simulation with specific duration
  python -m src.cli.simulate --profile live_eth --duration 4
  
  # Simulation with custom log file
  python -m src.cli.simulate --profile live_eth --log-file simulation.log
        """
    )
    
    # Configuration options
    parser.add_argument(
        "--profile", "-p",
        default="live_eth",
        help="Configuration profile to use for simulation (default: live_eth)"
    )
    
    parser.add_argument(
        "--fallback", "-f",
        help="Fallback configuration profile"
    )
    
    # Trading parameters
    parser.add_argument(
        "--market", "-m",
        help="Market to simulate (e.g., ETH-PERP, BTC-PERP)"
    )
    
    parser.add_argument(
        "--timeframe", "-t",
        help="Timeframe to use (e.g., 1m, 15m, 1h, 4h)"
    )
    
    parser.add_argument(
        "--leverage", "-l",
        type=float,
        help="Leverage to use for simulation"
    )
    
    parser.add_argument(
        "--position-size", "-s",
        type=float,
        help="Position size as a decimal (0.0 to 1.0)"
    )
    
    parser.add_argument(
        "--capital", "-c",
        type=float,
        help="Initial capital for simulation"
    )
    
    # Simulation parameters
    parser.add_argument(
        "--duration", "-d",
        type=int,
        default=24,
        help="Duration to run simulation in hours (default: 24)"
    )
    
    parser.add_argument(
        "--max-trades",
        type=int,
        help="Maximum number of trades to execute"
    )
    
    parser.add_argument(
        "--strategy",
        choices=["bbrsi", "scalping"],
        help="Strategy to use for simulation"
    )
    
    # Output options
    parser.add_argument(
        "--output", "-o",
        help="Output file for simulation results (JSON format)"
    )
    
    parser.add_argument(
        "--log-file",
        help="Log file for simulation logging"
    )
    
    # Control options
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress all output except errors"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    logger = setup_logging(level=log_level, log_file=args.log_file)
    
    try:
        # Initialize configuration manager
        config_manager = ConfigManager()
        
        # Load configuration profile
        logger.info(f"Loading configuration profile: {args.profile}")
        config = config_manager.load_config(args.profile, fallback=args.fallback)
        
        # Override configuration with command line arguments
        if args.market:
            config['trading']['market'] = args.market
            logger.info(f"Market overridden to: {args.market}")
        
        if args.timeframe:
            config['trading']['timeframe'] = args.timeframe
            logger.info(f"Timeframe overridden to: {args.timeframe}")
        
        if args.leverage:
            config['trading']['leverage'] = args.leverage
            logger.info(f"Leverage overridden to: {args.leverage}")
        
        if args.position_size:
            config['trading']['positionSizePct'] = args.position_size
            logger.info(f"Position size overridden to: {args.position_size}")
        
        if args.capital:
            config['trading']['initialBalance'] = args.capital
            logger.info(f"Initial capital overridden to: {args.capital}")
        
        if args.strategy:
            config['strategy'] = args.strategy
            logger.info(f"Strategy overridden to: {args.strategy}")
        
        # Validate configuration
        is_valid, errors = config_manager.validate_config(config)
        if not is_valid:
            logger.error("Configuration validation failed:")
            for error in errors:
                logger.error(f"  - {error}")
            sys.exit(1)
        
        # Display configuration summary
        if not args.quiet:
            summary = config_manager.get_config_summary(args.profile)
            logger.info("Simulation Configuration:")
            logger.info(f"  Market: {summary['trading']['market']}")
            logger.info(f"  Timeframe: {summary['trading']['timeframe']}")
            logger.info(f"  Leverage: {summary['trading']['leverage']}")
            logger.info(f"  Position Size: {summary['trading']['position_size']}")
            logger.info(f"  Strategy: {config.get('strategy', 'bbrsi')}")
            logger.info(f"  Duration: {args.duration} hours")
            if args.max_trades:
                logger.info(f"  Max Trades: {args.max_trades}")
        
        # Initialize exchange clients
        logger.info("Initializing exchange clients...")
        info = setup_clients()
        exchange = Exchange(info)
        
        # Create and run simulation
        logger.info("Starting live simulation...")
        trader = LiveSimulationCLI(exchange=exchange, config=config, info=info)
        
        # Run simulation
        asyncio.run(trader.run(duration_hours=args.duration, max_trades=args.max_trades))
        
        logger.info("Live simulation completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("Simulation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        if args.verbose:
            import traceback
            logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    simulate_cli()
