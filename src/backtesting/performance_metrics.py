"""
Comprehensive Performance Metrics Calculator

Calculates advanced performance metrics for backtesting results:
- Risk-adjusted returns (Sharpe, Sortino, Calmar ratios)
- Drawdown analysis
- Trade statistics
- Value at Risk (VaR)
- Expected Shortfall
"""

import numpy as np
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics."""
    # Returns
    total_return: float
    annualized_return: float
    average_return_per_trade: float
    
    # Risk metrics
    volatility: float
    max_drawdown: float
    max_drawdown_duration: int
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    
    # Trade statistics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    average_win: float
    average_loss: float
    largest_win: float
    largest_loss: float
    
    # Risk measures
    var_95: float  # Value at Risk at 95% confidence
    var_99: float  # Value at Risk at 99% confidence
    expected_shortfall_95: float
    expected_shortfall_99: float
    
    # Exposure
    average_exposure: float
    max_exposure: float
    exposure_time: float  # Percentage of time in market
    
    # Additional metrics
    recovery_factor: float
    ulcer_index: float
    kelly_percentage: float


class PerformanceMetricsCalculator:
    """Calculate comprehensive performance metrics."""
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize metrics calculator.
        
        Args:
            risk_free_rate: Risk-free rate for Sharpe/Sortino calculations (annual)
        """
        self.risk_free_rate = risk_free_rate
    
    def calculate(
        self,
        equity_curve: List[float],
        trades: List[Dict[str, Any]],
        initial_capital: float
    ) -> PerformanceMetrics:
        """
        Calculate comprehensive performance metrics.
        
        Args:
            equity_curve: List of equity values over time
            trades: List of trade dictionaries
            initial_capital: Initial capital
            
        Returns:
            PerformanceMetrics object
        """
        if not equity_curve or len(equity_curve) < 2:
            raise ValueError("Equity curve must have at least 2 data points")
        
        equity_array = np.array(equity_curve)
        
        # Calculate returns
        returns = self._calculate_returns(equity_array)
        
        # Trade statistics
        trade_stats = self._calculate_trade_statistics(trades)
        
        # Risk metrics
        risk_metrics = self._calculate_risk_metrics(returns, equity_array, initial_capital)
        
        # Exposure metrics
        exposure_metrics = self._calculate_exposure_metrics(trades, len(equity_curve))
        
        # Combine all metrics
        return PerformanceMetrics(
            # Returns
            total_return=risk_metrics['total_return'],
            annualized_return=risk_metrics['annualized_return'],
            average_return_per_trade=trade_stats['avg_return_per_trade'],
            
            # Risk metrics
            volatility=risk_metrics['volatility'],
            max_drawdown=risk_metrics['max_drawdown'],
            max_drawdown_duration=risk_metrics['max_drawdown_duration'],
            sharpe_ratio=risk_metrics['sharpe_ratio'],
            sortino_ratio=risk_metrics['sortino_ratio'],
            calmar_ratio=risk_metrics['calmar_ratio'],
            
            # Trade statistics
            total_trades=trade_stats['total_trades'],
            winning_trades=trade_stats['winning_trades'],
            losing_trades=trade_stats['losing_trades'],
            win_rate=trade_stats['win_rate'],
            profit_factor=trade_stats['profit_factor'],
            average_win=trade_stats['avg_win'],
            average_loss=trade_stats['avg_loss'],
            largest_win=trade_stats['largest_win'],
            largest_loss=trade_stats['largest_loss'],
            
            # Risk measures
            var_95=risk_metrics['var_95'],
            var_99=risk_metrics['var_99'],
            expected_shortfall_95=risk_metrics['es_95'],
            expected_shortfall_99=risk_metrics['es_99'],
            
            # Exposure
            average_exposure=exposure_metrics['avg_exposure'],
            max_exposure=exposure_metrics['max_exposure'],
            exposure_time=exposure_metrics['exposure_time'],
            
            # Additional metrics
            recovery_factor=risk_metrics['recovery_factor'],
            ulcer_index=risk_metrics['ulcer_index'],
            kelly_percentage=trade_stats['kelly_percentage']
        )
    
    def _calculate_returns(self, equity_array: np.ndarray) -> np.ndarray:
        """Calculate period returns from equity curve."""
        returns = np.diff(equity_array) / equity_array[:-1]
        return returns
    
    def _calculate_trade_statistics(self, trades: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate trade-level statistics."""
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'largest_win': 0.0,
                'largest_loss': 0.0,
                'avg_return_per_trade': 0.0,
                'kelly_percentage': 0.0
            }
        
        profits = []
        wins = []
        losses = []
        
        for trade in trades:
            pnl = trade.get('profit', trade.get('pnl', 0.0))
            profits.append(pnl)
            
            if pnl > 0:
                wins.append(pnl)
            elif pnl < 0:
                losses.append(abs(pnl))
        
        total_trades = len(trades)
        winning_trades = len(wins)
        losing_trades = len(losses)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0.0
        
        avg_win = np.mean(wins) if wins else 0.0
        avg_loss = np.mean(losses) if losses else 0.0
        largest_win = max(wins) if wins else 0.0
        largest_loss = max(losses) if losses else 0.0
        
        gross_profit = sum(wins) if wins else 0.0
        gross_loss = sum(losses) if losses else 0.0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        avg_return_per_trade = np.mean(profits) if profits else 0.0
        
        # Kelly percentage
        if win_rate > 0 and avg_loss > 0:
            kelly = win_rate - ((1 - win_rate) / (avg_win / avg_loss))
            kelly_percentage = max(0.0, min(kelly, 1.0))  # Clamp between 0 and 1
        else:
            kelly_percentage = 0.0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'largest_win': largest_win,
            'largest_loss': largest_loss,
            'avg_return_per_trade': avg_return_per_trade,
            'kelly_percentage': kelly_percentage
        }
    
    def _calculate_risk_metrics(
        self,
        returns: np.ndarray,
        equity_array: np.ndarray,
        initial_capital: float
    ) -> Dict[str, float]:
        """Calculate risk-adjusted metrics."""
        if len(returns) == 0:
            return self._empty_risk_metrics()
        
        # Total return
        total_return = (equity_array[-1] - initial_capital) / initial_capital
        
        # Annualized return (assuming daily returns)
        periods_per_year = 252  # Trading days
        if len(returns) > 0:
            annualized_return = np.mean(returns) * periods_per_year
        else:
            annualized_return = 0.0
        
        # Volatility
        volatility = np.std(returns) * np.sqrt(periods_per_year) if len(returns) > 1 else 0.0
        
        # Drawdown calculation
        drawdown_info = self._calculate_drawdown(equity_array, initial_capital)
        max_drawdown = drawdown_info['max_drawdown']
        max_drawdown_duration = drawdown_info['max_drawdown_duration']
        
        # Sharpe ratio
        if volatility > 0:
            sharpe_ratio = (annualized_return - self.risk_free_rate) / volatility
        else:
            sharpe_ratio = 0.0
        
        # Sortino ratio (downside deviation)
        downside_returns = returns[returns < 0]
        if len(downside_returns) > 0:
            downside_std = np.std(downside_returns) * np.sqrt(periods_per_year)
            sortino_ratio = (annualized_return - self.risk_free_rate) / downside_std if downside_std > 0 else 0.0
        else:
            sortino_ratio = float('inf') if annualized_return > self.risk_free_rate else 0.0
        
        # Calmar ratio
        if abs(max_drawdown) > 0:
            calmar_ratio = annualized_return / abs(max_drawdown)
        else:
            calmar_ratio = float('inf') if annualized_return > 0 else 0.0
        
        # Value at Risk (VaR)
        var_95 = np.percentile(returns, 5) if len(returns) > 0 else 0.0
        var_99 = np.percentile(returns, 1) if len(returns) > 0 else 0.0
        
        # Expected Shortfall (Conditional VaR)
        es_95 = np.mean(returns[returns <= var_95]) if len(returns[returns <= var_95]) > 0 else 0.0
        es_99 = np.mean(returns[returns <= var_99]) if len(returns[returns <= var_99]) > 0 else 0.0
        
        # Recovery factor
        recovery_factor = total_return / abs(max_drawdown) if abs(max_drawdown) > 0 else float('inf')
        
        # Ulcer Index
        ulcer_index = self._calculate_ulcer_index(equity_array, initial_capital)
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'max_drawdown': max_drawdown,
            'max_drawdown_duration': max_drawdown_duration,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'var_95': var_95,
            'var_99': var_99,
            'es_95': es_95,
            'es_99': es_99,
            'recovery_factor': recovery_factor,
            'ulcer_index': ulcer_index
        }
    
    def _calculate_drawdown(self, equity_array: np.ndarray, initial_capital: float) -> Dict[str, float]:
        """Calculate drawdown metrics."""
        # Calculate running maximum
        running_max = np.maximum.accumulate(equity_array)
        
        # Calculate drawdown
        drawdown = (equity_array - running_max) / running_max
        
        max_drawdown = np.min(drawdown)
        
        # Calculate max drawdown duration
        max_dd_idx = np.argmin(drawdown)
        # Find when equity recovered to previous high
        recovery_idx = None
        for i in range(max_dd_idx + 1, len(equity_array)):
            if equity_array[i] >= running_max[max_dd_idx]:
                recovery_idx = i
                break
        
        if recovery_idx:
            max_drawdown_duration = recovery_idx - max_dd_idx
        else:
            max_drawdown_duration = len(equity_array) - max_dd_idx
        
        return {
            'max_drawdown': max_drawdown,
            'max_drawdown_duration': max_drawdown_duration
        }
    
    def _calculate_ulcer_index(self, equity_array: np.ndarray, initial_capital: float) -> float:
        """Calculate Ulcer Index (measure of drawdown severity)."""
        running_max = np.maximum.accumulate(equity_array)
        drawdown_pct = ((equity_array - running_max) / running_max) * 100
        
        # Square of drawdown percentages
        squared_dd = drawdown_pct ** 2
        
        # Average of squared drawdowns
        ulcer_index = np.sqrt(np.mean(squared_dd))
        
        return ulcer_index
    
    def _calculate_exposure_metrics(self, trades: List[Dict[str, Any]], total_periods: int) -> Dict[str, float]:
        """Calculate exposure metrics."""
        if not trades or total_periods == 0:
            return {
                'avg_exposure': 0.0,
                'max_exposure': 0.0,
                'exposure_time': 0.0
            }
        
        # Calculate exposure over time (simplified - assumes positions held until next trade)
        exposures = []
        in_market_periods = 0
        
        for trade in trades:
            size = abs(trade.get('size', 0.0))
            exposures.append(size)
            if size > 0:
                in_market_periods += 1
        
        avg_exposure = np.mean(exposures) if exposures else 0.0
        max_exposure = max(exposures) if exposures else 0.0
        exposure_time = in_market_periods / total_periods if total_periods > 0 else 0.0
        
        return {
            'avg_exposure': avg_exposure,
            'max_exposure': max_exposure,
            'exposure_time': exposure_time
        }
    
    def _empty_risk_metrics(self) -> Dict[str, float]:
        """Return empty risk metrics."""
        return {
            'total_return': 0.0,
            'annualized_return': 0.0,
            'volatility': 0.0,
            'max_drawdown': 0.0,
            'max_drawdown_duration': 0,
            'sharpe_ratio': 0.0,
            'sortino_ratio': 0.0,
            'calmar_ratio': 0.0,
            'var_95': 0.0,
            'var_99': 0.0,
            'es_95': 0.0,
            'es_99': 0.0,
            'recovery_factor': 0.0,
            'ulcer_index': 0.0
        }
    
    def format_metrics(self, metrics: PerformanceMetrics) -> Dict[str, Any]:
        """Format metrics for display."""
        return {
            'returns': {
                'total_return': f"{metrics.total_return:.2%}",
                'annualized_return': f"{metrics.annualized_return:.2%}",
                'average_return_per_trade': f"{metrics.average_return_per_trade:.2f}"
            },
            'risk': {
                'volatility': f"{metrics.volatility:.2%}",
                'max_drawdown': f"{metrics.max_drawdown:.2%}",
                'max_drawdown_duration': f"{metrics.max_drawdown_duration} periods",
                'sharpe_ratio': f"{metrics.sharpe_ratio:.3f}",
                'sortino_ratio': f"{metrics.sortino_ratio:.3f}",
                'calmar_ratio': f"{metrics.calmar_ratio:.3f}"
            },
            'trades': {
                'total_trades': metrics.total_trades,
                'win_rate': f"{metrics.win_rate:.2%}",
                'profit_factor': f"{metrics.profit_factor:.2f}",
                'average_win': f"{metrics.average_win:.2f}",
                'average_loss': f"{metrics.average_loss:.2f}"
            },
            'risk_measures': {
                'var_95': f"{metrics.var_95:.2%}",
                'var_99': f"{metrics.var_99:.2%}",
                'expected_shortfall_95': f"{metrics.expected_shortfall_95:.2%}",
                'expected_shortfall_99': f"{metrics.expected_shortfall_99:.2%}"
            },
            'exposure': {
                'average_exposure': f"{metrics.average_exposure:.2f}",
                'max_exposure': f"{metrics.max_exposure:.2f}",
                'exposure_time': f"{metrics.exposure_time:.2%}"
            },
            'additional': {
                'recovery_factor': f"{metrics.recovery_factor:.2f}",
                'ulcer_index': f"{metrics.ulcer_index:.2f}",
                'kelly_percentage': f"{metrics.kelly_percentage:.2%}"
            }
        }


