"""
Performance Calculation Utilities

This module provides utilities for calculating trading performance metrics.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

def calculate_metrics(trades: List[Dict[str, Any]], 
                     initial_capital: float = 10000.0) -> Dict[str, Any]:
    """
    Calculate comprehensive trading performance metrics.
    
    Args:
        trades: List of trade dictionaries
        initial_capital: Starting capital amount
        
    Returns:
        Dictionary containing all performance metrics
    """
    if not trades:
        return _empty_metrics(initial_capital)
    
    # Extract trade data
    pnl_list = [trade.get('pnl', 0.0) for trade in trades]
    entry_prices = [trade.get('entry_price', 0.0) for trade in trades]
    exit_prices = [trade.get('exit_price', 0.0) for trade in trades]
    entry_times = [trade.get('entry_time', 0) for trade in trades]
    exit_times = [trade.get('exit_time', 0) for trade in trades]
    durations = [trade.get('duration', 0) for trade in trades]
    
    # Basic metrics
    total_trades = len(trades)
    winning_trades = len([pnl for pnl in pnl_list if pnl > 0])
    losing_trades = len([pnl for pnl in pnl_list if pnl < 0])
    breakeven_trades = len([pnl for pnl in pnl_list if pnl == 0])
    
    # P&L metrics
    total_pnl = sum(pnl_list)
    gross_profit = sum([pnl for pnl in pnl_list if pnl > 0])
    gross_loss = abs(sum([pnl for pnl in pnl_list if pnl < 0]))
    
    # Win rate and profit factor
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float('inf')
    
    # Risk metrics
    max_drawdown, drawdown_percentage = calculate_max_drawdown(pnl_list, initial_capital)
    
    # Calculate equity curve
    equity_curve = calculate_equity_curve(pnl_list, initial_capital)
    
    # Calculate returns
    returns = calculate_returns(equity_curve)
    
    # Risk-adjusted metrics
    sharpe_ratio = calculate_sharpe_ratio(returns)
    calmar_ratio = calculate_calmar_ratio(total_pnl, max_drawdown)
    sortino_ratio = calculate_sortino_ratio(returns)
    
    # Trade analysis
    win_loss_ratio = calculate_win_loss_ratio(pnl_list)
    consecutive_stats = calculate_consecutive_wins_losses(pnl_list)
    risk_reward_ratio = calculate_risk_reward_ratio(pnl_list)
    
    # Time analysis
    avg_duration = np.mean(durations) if durations else 0.0
    total_duration = sum(durations) if durations else 0.0
    
    # Price analysis
    avg_entry_price = np.mean(entry_prices) if entry_prices else 0.0
    avg_exit_price = np.mean(exit_prices) if exit_prices else 0.0
    
    return {
        'summary': {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'breakeven_trades': breakeven_trades,
            'win_rate': round(win_rate, 2),
            'total_pnl': round(total_pnl, 2),
            'final_capital': round(initial_capital + total_pnl, 2),
            'return_percentage': round((total_pnl / initial_capital) * 100, 2)
        },
        'pnl_analysis': {
            'gross_profit': round(gross_profit, 2),
            'gross_loss': round(gross_loss, 2),
            'net_profit': round(total_pnl, 2),
            'profit_factor': round(profit_factor, 2) if profit_factor != float('inf') else 'inf',
            'avg_win': round(gross_profit / winning_trades, 2) if winning_trades > 0 else 0.0,
            'avg_loss': round(gross_loss / losing_trades, 2) if losing_trades > 0 else 0.0
        },
        'risk_metrics': {
            'max_drawdown': round(max_drawdown, 2),
            'max_drawdown_percentage': round(drawdown_percentage, 2),
            'sharpe_ratio': round(sharpe_ratio, 3),
            'calmar_ratio': round(calmar_ratio, 3),
            'sortino_ratio': round(sortino_ratio, 3)
        },
        'trade_analysis': {
            'win_loss_ratio': round(win_loss_ratio, 2),
            'risk_reward_ratio': round(risk_reward_ratio, 2),
            'consecutive_wins': consecutive_stats['max_consecutive_wins'],
            'consecutive_losses': consecutive_stats['max_consecutive_losses'],
            'avg_duration': round(avg_duration, 2),
            'total_duration': round(total_duration, 2)
        },
        'equity_curve': equity_curve,
        'returns': returns
    }

def _empty_metrics(initial_capital: float) -> Dict[str, Any]:
    """Return empty metrics structure for no trades."""
    return {
        'summary': {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'breakeven_trades': 0,
            'win_rate': 0.0,
            'total_pnl': 0.0,
            'final_capital': initial_capital,
            'return_percentage': 0.0
        },
        'pnl_analysis': {
            'gross_profit': 0.0,
            'gross_loss': 0.0,
            'net_profit': 0.0,
            'profit_factor': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0
        },
        'risk_metrics': {
            'max_drawdown': 0.0,
            'max_drawdown_percentage': 0.0,
            'sharpe_ratio': 0.0,
            'calmar_ratio': 0.0,
            'sortino_ratio': 0.0
        },
        'trade_analysis': {
            'win_loss_ratio': 0.0,
            'risk_reward_ratio': 0.0,
            'consecutive_wins': 0,
            'consecutive_losses': 0,
            'avg_duration': 0.0,
            'total_duration': 0.0
        },
        'equity_curve': [initial_capital],
        'returns': [0.0]
    }

def calculate_equity_curve(pnl_list: List[float], 
                          initial_capital: float) -> List[float]:
    """
    Calculate equity curve from P&L list.
    
    Args:
        pnl_list: List of P&L values
        initial_capital: Starting capital
        
    Returns:
        List of equity values
    """
    equity = [initial_capital]
    current_capital = initial_capital
    
    for pnl in pnl_list:
        current_capital += pnl
        equity.append(current_capital)
    
    return equity

def calculate_max_drawdown(pnl_list: List[float], 
                          initial_capital: float) -> Tuple[float, float]:
    """
    Calculate maximum drawdown and percentage.
    
    Args:
        pnl_list: List of P&L values
        initial_capital: Starting capital
        
    Returns:
        Tuple of (max_drawdown, max_drawdown_percentage)
    """
    equity_curve = calculate_equity_curve(pnl_list, initial_capital)
    
    if not equity_curve:
        return 0.0, 0.0
    
    peak = equity_curve[0]
    max_drawdown = 0.0
    
    for equity in equity_curve:
        if equity > peak:
            peak = equity
        drawdown = peak - equity
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    
    max_drawdown_percentage = (max_drawdown / peak * 100) if peak > 0 else 0.0
    
    return max_drawdown, max_drawdown_percentage

def calculate_returns(equity_curve: List[float]) -> List[float]:
    """
    Calculate percentage returns from equity curve.
    
    Args:
        equity_curve: List of equity values
        
    Returns:
        List of percentage returns
    """
    if len(equity_curve) < 2:
        return [0.0]
    
    returns = []
    for i in range(1, len(equity_curve)):
        if equity_curve[i-1] != 0:
            ret = (equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1]
            returns.append(ret)
        else:
            returns.append(0.0)
    
    return returns

def calculate_sharpe_ratio(returns: List[float], 
                          risk_free_rate: float = 0.0) -> float:
    """
    Calculate Sharpe ratio.
    
    Args:
        returns: List of returns
        risk_free_rate: Risk-free rate (default: 0.0)
        
    Returns:
        Sharpe ratio
    """
    if not returns:
        return 0.0
    
    returns_array = np.array(returns)
    excess_returns = returns_array - risk_free_rate
    
    if len(excess_returns) < 2:
        return 0.0
    
    mean_return = np.mean(excess_returns)
    std_return = np.std(excess_returns, ddof=1)
    
    if std_return == 0:
        return 0.0
    
    # Annualize (assuming daily returns)
    sharpe_ratio = (mean_return / std_return) * np.sqrt(252)
    
    return float(sharpe_ratio)

def calculate_calmar_ratio(total_return: float, 
                          max_drawdown: float) -> float:
    """
    Calculate Calmar ratio.
    
    Args:
        total_return: Total return amount
        max_drawdown: Maximum drawdown amount
        
    Returns:
        Calmar ratio
    """
    if max_drawdown == 0:
        return 0.0
    
    # Annualize (assuming 1 year period)
    calmar_ratio = (total_return / max_drawdown) * 1.0
    
    return float(calmar_ratio)

def calculate_sortino_ratio(returns: List[float], 
                           risk_free_rate: float = 0.0) -> float:
    """
    Calculate Sortino ratio.
    
    Args:
        returns: List of returns
        risk_free_rate: Risk-free rate (default: 0.0)
        
    Returns:
        Sortino ratio
    """
    if not returns:
        return 0.0
    
    returns_array = np.array(returns)
    excess_returns = returns_array - risk_free_rate
    
    if len(excess_returns) < 2:
        return 0.0
    
    mean_return = np.mean(excess_returns)
    
    # Calculate downside deviation (only negative returns)
    downside_returns = excess_returns[excess_returns < 0]
    
    if len(downside_returns) == 0:
        return 0.0
    
    downside_deviation = np.std(downside_returns, ddof=1)
    
    if downside_deviation == 0:
        return 0.0
    
    # Annualize (assuming daily returns)
    sortino_ratio = (mean_return / downside_deviation) * np.sqrt(252)
    
    return float(sortino_ratio)

def calculate_win_loss_ratio(pnl_list: List[float]) -> float:
    """
    Calculate win/loss ratio.
    
    Args:
        pnl_list: List of P&L values
        
    Returns:
        Win/loss ratio
    """
    winning_trades = [pnl for pnl in pnl_list if pnl > 0]
    losing_trades = [pnl for pnl in pnl_list if pnl < 0]
    
    if not losing_trades:
        return float('inf') if winning_trades else 0.0
    
    avg_win = np.mean(winning_trades) if winning_trades else 0.0
    avg_loss = abs(np.mean(losing_trades))
    
    return float(avg_win / avg_loss) if avg_loss > 0 else 0.0

def calculate_consecutive_wins_losses(pnl_list: List[float]) -> Dict[str, int]:
    """
    Calculate consecutive wins and losses.
    
    Args:
        pnl_list: List of P&L values
        
    Returns:
        Dictionary with consecutive counts
    """
    if not pnl_list:
        return {'max_consecutive_wins': 0, 'max_consecutive_losses': 0}
    
    max_consecutive_wins = 0
    max_consecutive_losses = 0
    current_wins = 0
    current_losses = 0
    
    for pnl in pnl_list:
        if pnl > 0:
            current_wins += 1
            current_losses = 0
            max_consecutive_wins = max(max_consecutive_wins, current_wins)
        elif pnl < 0:
            current_losses += 1
            current_wins = 0
            max_consecutive_losses = max(max_consecutive_losses, current_losses)
        else:
            # Breakeven trade
            current_wins = 0
            current_losses = 0
    
    return {
        'max_consecutive_wins': max_consecutive_wins,
        'max_consecutive_losses': max_consecutive_losses
    }

def calculate_risk_reward_ratio(pnl_list: List[float]) -> float:
    """
    Calculate risk/reward ratio.
    
    Args:
        pnl_list: List of P&L values
        
    Returns:
        Risk/reward ratio
    """
    winning_trades = [pnl for pnl in pnl_list if pnl > 0]
    losing_trades = [pnl for pnl in pnl_list if pnl < 0]
    
    if not winning_trades or not losing_trades:
        return 0.0
    
    avg_win = np.mean(winning_trades)
    avg_loss = abs(np.mean(losing_trades))
    
    return float(avg_win / avg_loss) if avg_loss > 0 else 0.0

def calculate_position_sizing_metrics(trades: List[Dict[str, Any]], 
                                    initial_capital: float) -> Dict[str, Any]:
    """
    Calculate position sizing and risk metrics.
    
    Args:
        trades: List of trade dictionaries
        initial_capital: Starting capital
        
    Returns:
        Dictionary with position sizing metrics
    """
    if not trades:
        return {}
    
    # Extract position sizes and risk data
    position_sizes = []
    risk_per_trade = []
    
    for trade in trades:
        if 'position_size' in trade:
            position_sizes.append(trade['position_size'])
        if 'risk_amount' in trade:
            risk_per_trade.append(trade['risk_amount'])
    
    metrics = {}
    
    if position_sizes:
        metrics['avg_position_size'] = round(np.mean(position_sizes), 2)
        metrics['max_position_size'] = round(max(position_sizes), 2)
        metrics['min_position_size'] = round(min(position_sizes), 2)
        metrics['position_size_std'] = round(np.std(position_sizes), 2)
    
    if risk_per_trade:
        metrics['avg_risk_per_trade'] = round(np.mean(risk_per_trade), 2)
        metrics['max_risk_per_trade'] = round(max(risk_per_trade), 2)
        metrics['total_risk'] = round(sum(risk_per_trade), 2)
        metrics['risk_percentage'] = round((sum(risk_per_trade) / initial_capital) * 100, 2)
    
    return metrics

def generate_performance_report(metrics: Dict[str, Any], 
                              output_file: Optional[str] = None) -> str:
    """
    Generate a formatted performance report.
    
    Args:
        metrics: Performance metrics dictionary
        output_file: Optional file path to save report
        
    Returns:
        Formatted report string
    """
    report = []
    report.append("=" * 60)
    report.append("TRADING PERFORMANCE REPORT")
    report.append("=" * 60)
    
    # Summary
    summary = metrics.get('summary', {})
    report.append(f"\nSUMMARY:")
    report.append(f"  Total Trades: {summary.get('total_trades', 0)}")
    report.append(f"  Win Rate: {summary.get('win_rate', 0.0)}%")
    report.append(f"  Total P&L: ${summary.get('total_pnl', 0.0):,.2f}")
    report.append(f"  Final Capital: ${summary.get('final_capital', 0.0):,.2f}")
    report.append(f"  Return: {summary.get('return_percentage', 0.0)}%")
    
    # P&L Analysis
    pnl_analysis = metrics.get('pnl_analysis', {})
    report.append(f"\nP&L ANALYSIS:")
    report.append(f"  Gross Profit: ${pnl_analysis.get('gross_profit', 0.0):,.2f}")
    report.append(f"  Gross Loss: ${pnl_analysis.get('gross_loss', 0.0):,.2f}")
    report.append(f"  Profit Factor: {pnl_analysis.get('profit_factor', 0.0)}")
    report.append(f"  Average Win: ${pnl_analysis.get('avg_win', 0.0):,.2f}")
    report.append(f"  Average Loss: ${pnl_analysis.get('avg_loss', 0.0):,.2f}")
    
    # Risk Metrics
    risk_metrics = metrics.get('risk_metrics', {})
    report.append(f"\nRISK METRICS:")
    report.append(f"  Max Drawdown: ${risk_metrics.get('max_drawdown', 0.0):,.2f} ({risk_metrics.get('max_drawdown_percentage', 0.0)}%)")
    report.append(f"  Sharpe Ratio: {risk_metrics.get('sharpe_ratio', 0.0)}")
    report.append(f"  Calmar Ratio: {risk_metrics.get('calmar_ratio', 0.0)}")
    report.append(f"  Sortino Ratio: {risk_metrics.get('sortino_ratio', 0.0)}")
    
    # Trade Analysis
    trade_analysis = metrics.get('trade_analysis', {})
    report.append(f"\nTRADE ANALYSIS:")
    report.append(f"  Win/Loss Ratio: {trade_analysis.get('win_loss_ratio', 0.0)}")
    report.append(f"  Risk/Reward Ratio: {trade_analysis.get('risk_reward_ratio', 0.0)}")
    report.append(f"  Max Consecutive Wins: {trade_analysis.get('consecutive_wins', 0)}")
    report.append(f"  Max Consecutive Losses: {trade_analysis.get('consecutive_losses', 0)}")
    
    report.append("\n" + "=" * 60)
    
    report_text = "\n".join(report)
    
    # Save to file if specified
    if output_file:
        try:
            with open(output_file, 'w') as f:
                f.write(report_text)
            logger.info(f"Performance report saved to {output_file}")
        except Exception as e:
            logger.error(f"Failed to save performance report: {e}")
    
    return report_text
