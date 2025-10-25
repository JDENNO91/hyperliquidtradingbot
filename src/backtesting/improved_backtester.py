"""
Improved Backtester

A robust backtesting system with proper position management and performance tracking.
"""

import asyncio
import logging
import json
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.improved_trading_engine import ImprovedTradingEngine
from core.base_strategy import BaseStrategy
from strategies import StrategyFactory
from config import ConfigManager
from utils import setup_logger, load_market_data, calculate_metrics, generate_performance_report

logger = logging.getLogger(__name__)

class ImprovedBacktester:
    """
    Improved backtesting system with robust position management.
    
    This backtester provides:
    - Reliable position tracking and management
    - Proper signal execution and position lifecycle
    - Comprehensive performance analysis
    - Clean error handling and logging
    - Detailed trade history and statistics
    """
    
    def __init__(self, config_path: str, log_level: str = "INFO", log_file: str = None):
        """
        Initialize the improved backtester.
        
        Args:
            config_path: Path to configuration file
            log_level: Logging level
            log_file: Optional log file path
        """
        # Setup logging
        setup_logger(name=__name__, level=log_level, log_file=log_file)
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config_manager = ConfigManager()
        self.config = self._load_config(config_path)
        
        # Initialize trading engine
        self.trading_engine = ImprovedTradingEngine(self.config)
        
        # Load strategy
        self.strategy = self._load_strategy()
        self.trading_engine.set_strategy(self.strategy)
        
        # Performance tracking
        self.results = {}
        self.start_time = None
        self.end_time = None
        
        self.logger.info("Improved backtester initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load and validate configuration.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        try:
            # Load config file
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Merge with defaults
            default_config = self.config_manager.get_default_config()
            merged_config = self._merge_configs(default_config, config)
            
            # Validate critical config values
            self._validate_critical_config(merged_config)
            
            # Validate config using config manager
            is_valid = self.config_manager.validate_config(merged_config)
            if not is_valid:
                self.logger.warning("Configuration validation failed, using as-is")
            
            self.logger.info(f"Configuration loaded from {config_path}")
            return merged_config
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise
    
    def _merge_configs(self, default_config: Dict[str, Any], user_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge user configuration with defaults.
        
        Args:
            default_config: Default configuration
            user_config: User configuration
            
        Returns:
            Merged configuration
        """
        merged = default_config.copy()
        
        for key, value in user_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def _validate_critical_config(self, config: Dict[str, Any]) -> None:
        """
        Validate critical configuration values.
        
        Args:
            config: Configuration to validate
        """
        # Check for initial capital in various possible locations
        initial_capital = None
        if 'initial_capital' in config:
            initial_capital = config['initial_capital']
        elif 'backtest' in config and 'initialCapital' in config['backtest']:
            initial_capital = config['backtest']['initialCapital']
        elif 'initialCapital' in config:
            initial_capital = config['initialCapital']
        
        if initial_capital is None:
            raise ValueError("Missing required configuration field: initial_capital (or initialCapital)")
        
        if initial_capital <= 0:
            raise ValueError("Initial capital must be positive")
        
        # Normalize the config to use initial_capital
        config['initial_capital'] = initial_capital
        
        # Check for strategy
        if 'strategy' not in config:
            raise ValueError("Missing required configuration field: strategy")
    
    def _load_strategy(self) -> BaseStrategy:
        """
        Load and initialize the trading strategy.
        
        Returns:
            Strategy instance
        """
        try:
            strategy_name = self.config.get('strategy', 'bbrsi')
            strategy = StrategyFactory.create_strategy(strategy_name, self.config, self.logger)
            
            self.logger.info(f"Strategy loaded: {strategy.__class__.__name__}")
            return strategy
            
        except Exception as e:
            self.logger.error(f"Failed to load strategy: {e}")
            raise
    
    async def run_backtest(self, data_file: str) -> Dict[str, Any]:
        """
        Run a backtest with the specified data file.
        
        Args:
            data_file: Path to market data file
            
        Returns:
            Backtest results dictionary
        """
        self.logger.info(f"Starting backtest with data file: {data_file}")
        
        try:
            # Load market data
            market_data = load_market_data(data_file)
            if not market_data:
                raise ValueError("No market data loaded")
            
            self.logger.info(f"Loaded {len(market_data)} data points")
            
            # Start trading engine
            self.trading_engine.start()
            self.start_time = time.time()
            
            # Process market data
            for i, candle in enumerate(market_data):
                try:
                    # Process market data through trading engine
                    self.trading_engine.process_market_data(candle)
                    
                    # Log progress every 100 candles
                    if (i + 1) % 100 == 0:
                        self.logger.info(f"Processed {i + 1}/{len(market_data)} candles")
                
                except Exception as e:
                    self.logger.error(f"Error processing candle {i}: {e}")
                    continue
            
            # Stop trading engine
            self.trading_engine.stop()
            self.end_time = time.time()
            
            # Generate results
            self.results = self._generate_results(market_data)
            
            self.logger.info("Backtest completed successfully")
            return self.results
            
        except Exception as e:
            self.logger.error(f"Backtest failed: {e}")
            raise
    
    def _generate_results(self, market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate comprehensive backtest results.
        
        Args:
            market_data: Market data used in backtest
            
        Returns:
            Results dictionary
        """
        # Get engine performance stats
        engine_stats = self.trading_engine.get_performance_stats()
        
        # Get position statistics
        position_stats = self.trading_engine.position_manager.get_position_statistics()
        
        # Get closed positions for trade analysis
        closed_positions = self.trading_engine.position_manager.get_closed_positions()
        
        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(closed_positions, market_data)
        
        # Generate summary
        summary = self._generate_summary(engine_stats, position_stats, performance_metrics)
        
        return {
            'backtest_info': {
                'data_points': len(market_data),
                'start_time': market_data[0].get('timestamp', 0) if market_data else 0,
                'end_time': market_data[-1].get('timestamp', 0) if market_data else 0,
                'strategy': self.strategy.__class__.__name__,
                'duration_seconds': self.end_time - self.start_time if self.end_time and self.start_time else 0
            },
            'trades': [self._position_to_dict(pos) for pos in closed_positions],
            'performance': performance_metrics,
            'engine_stats': engine_stats,
            'position_stats': position_stats,
            'strategy_stats': self.strategy.get_performance_stats() if hasattr(self.strategy, 'get_performance_stats') else {},
            'summary': summary
        }
    
    def _calculate_performance_metrics(self, closed_positions: List, market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate comprehensive performance metrics.
        
        Args:
            closed_positions: List of closed positions
            market_data: Market data used in backtest
            
        Returns:
            Performance metrics dictionary
        """
        if not closed_positions:
            return {
                'summary': {
                    'total_trades': 0,
                    'win_rate': 0.0,
                    'net_profit': 0.0,
                    'final_capital': self.config['initial_capital'],
                    'return': 0.0
                },
                'risk_metrics': {
                    'max_drawdown': 0.0,
                    'sharpe_ratio': 0.0,
                    'profit_factor': 0.0
                }
            }
        
        # Basic trade statistics
        total_trades = len(closed_positions)
        winning_trades = len([p for p in closed_positions if p.pnl > 0])
        losing_trades = len([p for p in closed_positions if p.pnl < 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0
        
        # P&L analysis
        total_pnl = sum(p.pnl for p in closed_positions)
        gross_profit = sum(p.pnl for p in closed_positions if p.pnl > 0)
        gross_loss = abs(sum(p.pnl for p in closed_positions if p.pnl < 0))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Risk metrics
        equity_curve = [self.config['initial_capital']]
        current_capital = self.config['initial_capital']
        
        for position in closed_positions:
            current_capital += position.pnl
            equity_curve.append(current_capital)
        
        max_drawdown = self._calculate_max_drawdown(equity_curve)
        sharpe_ratio = self._calculate_sharpe_ratio(closed_positions)
        
        return {
            'summary': {
                'total_trades': total_trades,
                'win_rate': win_rate,
                'net_profit': total_pnl,
                'final_capital': current_capital,
                'return': (total_pnl / self.config['initial_capital']) * 100
            },
            'risk_metrics': {
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'profit_factor': profit_factor
            },
            'trade_analysis': {
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'breakeven_trades': total_trades - winning_trades - losing_trades,
                'gross_profit': gross_profit,
                'gross_loss': gross_loss,
                'average_win': gross_profit / max(winning_trades, 1),
                'average_loss': gross_loss / max(losing_trades, 1)
            },
            'equity_curve': equity_curve
        }
    
    def _calculate_max_drawdown(self, equity_curve: List[float]) -> float:
        """
        Calculate maximum drawdown from equity curve.
        
        Args:
            equity_curve: List of capital values over time
            
        Returns:
            Maximum drawdown percentage
        """
        if not equity_curve:
            return 0.0
        
        peak = equity_curve[0]
        max_dd = 0.0
        
        for value in equity_curve:
            if value > peak:
                peak = value
            else:
                drawdown = (peak - value) / peak * 100
                max_dd = max(max_dd, drawdown)
        
        return max_dd
    
    def _calculate_sharpe_ratio(self, closed_positions: List) -> float:
        """
        Calculate Sharpe ratio from closed positions.
        
        Args:
            closed_positions: List of closed positions
            
        Returns:
            Sharpe ratio
        """
        if len(closed_positions) < 2:
            return 0.0
        
        returns = [p.pnl for p in closed_positions]
        mean_return = sum(returns) / len(returns)
        
        if mean_return == 0:
            return 0.0
        
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        std_dev = variance ** 0.5
        
        if std_dev == 0:
            return 0.0
        
        return mean_return / std_dev
    
    def _position_to_dict(self, position) -> Dict[str, Any]:
        """
        Convert position object to dictionary.
        
        Args:
            position: Position object
            
        Returns:
            Position as dictionary
        """
        return {
            'id': position.id,
            'symbol': position.symbol,
            'side': position.side,
            'entry_price': position.entry_price,
            'exit_price': position.exit_price,
            'size': position.size,
            'notional': position.notional,
            'entry_time': position.entry_time,
            'exit_time': position.exit_time,
            'pnl': position.pnl,
            'stop_loss': position.stop_loss,
            'metadata': position.metadata
        }
    
    def _generate_summary(self, engine_stats: Dict[str, Any], position_stats: Dict[str, Any], 
                         performance_metrics: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary.
        
        Args:
            engine_stats: Engine statistics
            position_stats: Position statistics
            performance_metrics: Performance metrics
            
        Returns:
            Summary string
        """
        summary = performance_metrics['summary']
        risk_metrics = performance_metrics['risk_metrics']
        
        return (f"Backtest completed: {summary['total_trades']} trades, "
                f"{summary['win_rate']:.1f}% win rate, "
                f"${summary['net_profit']:.2f} P&L, "
                f"{summary['return']:.2f}% return, "
                f"{risk_metrics['max_drawdown']:.2f}% max drawdown")
    
    def get_summary(self) -> str:
        """
        Get a summary of the backtest results.
        
        Returns:
            Summary string
        """
        if not self.results:
            return "No backtest results available"
        
        return self.results.get('summary', 'No summary available')
    
    def save_results(self, output_file: str) -> None:
        """
        Save backtest results to file.
        
        Args:
            output_file: Path to output file
        """
        if not self.results:
            self.logger.warning("No results to save")
            return
        
        try:
            with open(output_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            
            self.logger.info(f"Results saved to {output_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")
            raise
    
    def print_summary(self) -> None:
        """Print a formatted summary of the backtest results."""
        if not self.results:
            print("No backtest results available")
            return
        
        backtest_info = self.results['backtest_info']
        performance = self.results['performance']
        
        print("=" * 60)
        print("Backtest Summary")
        print("=" * 60)
        print(f"Strategy: {backtest_info['strategy']}")
        print(f"Data Points: {backtest_info['data_points']}")
        print()
        print("Performance:")
        print(f"- Total Trades: {performance['summary']['total_trades']}")
        print(f"- Win Rate: {performance['summary']['win_rate']:.2f}%")
        print(f"- Net Profit: ${performance['summary']['net_profit']:.2f}")
        print(f"- Final Capital: ${performance['summary']['final_capital']:.2f}")
        print(f"- Return: {performance['summary']['return']:.2f}%")
        print()
        print("Risk Metrics:")
        print(f"- Max Drawdown: {performance['risk_metrics']['max_drawdown']:.2f}%")
        print(f"- Sharpe Ratio: {performance['risk_metrics']['sharpe_ratio']:.3f}")
        print(f"- Profit Factor: {performance['risk_metrics']['profit_factor']:.2f}")
        print("=" * 60)
