#!/usr/bin/env python3
"""
Performance Monitoring System

Provides comprehensive performance monitoring for live trading operations,
including real-time metrics, alerts, and performance analytics.
"""

import time
import threading
import json
import psutil
import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from collections import deque, defaultdict
import statistics

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    active_connections: int
    open_files: int
    thread_count: int

@dataclass
class TradingMetrics:
    """Trading-specific performance metrics."""
    timestamp: datetime
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_pnl: float
    unrealized_pnl: float
    realized_pnl: float
    max_drawdown: float
    current_drawdown: float
    win_rate: float
    profit_factor: float
    sharpe_ratio: float
    avg_trade_duration: float
    active_positions: int
    total_volume: float

@dataclass
class Alert:
    """Performance alert."""
    timestamp: datetime
    alert_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    message: str
    metric_name: str
    current_value: float
    threshold_value: float
    resolved: bool = False

class PerformanceMonitor:
    """Real-time performance monitoring system."""
    
    def __init__(self, log_dir: str = "logs", alert_callback: Optional[Callable] = None):
        """
        Initialize performance monitor.
        
        Args:
            log_dir: Directory for performance logs
            alert_callback: Callback function for alerts
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        self.alert_callback = alert_callback
        
        # Monitoring state
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Metrics storage
        self._system_metrics: deque = deque(maxlen=1000)  # Keep last 1000 measurements
        self._trading_metrics: deque = deque(maxlen=1000)
        self._alerts: List[Alert] = []
        
        # Performance thresholds
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'memory_used_mb': 2048.0,  # 2GB
            'disk_io_read_mb': 100.0,
            'disk_io_write_mb': 100.0,
            'network_sent_mb': 50.0,
            'network_recv_mb': 50.0,
            'active_connections': 100,
            'open_files': 1000,
            'thread_count': 50,
            'max_drawdown': 0.15,  # 15%
            'current_drawdown': 0.10,  # 10%
            'win_rate': 0.30,  # 30% minimum
            'profit_factor': 0.8,  # 0.8 minimum
            'sharpe_ratio': -1.0,  # -1.0 minimum
        }
        
        # Trading state tracking
        self._trading_state = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'unrealized_pnl': 0.0,
            'realized_pnl': 0.0,
            'max_drawdown': 0.0,
            'current_drawdown': 0.0,
            'peak_equity': 0.0,
            'active_positions': 0,
            'total_volume': 0.0,
            'trade_durations': deque(maxlen=1000),
            'pnl_history': deque(maxlen=1000)
        }
        
        # Network and disk I/O tracking
        self._last_network_stats = None
        self._last_disk_stats = None
    
    def start_monitoring(self, interval: float = 5.0):
        """
        Start performance monitoring.
        
        Args:
            interval: Monitoring interval in seconds
        """
        if self._monitoring:
            self.logger.warning("Performance monitoring already running")
            return
        
        self._monitoring = True
        self._stop_event.clear()
        
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self._monitor_thread.start()
        
        self.logger.info(f"Performance monitoring started with {interval}s interval")
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        if not self._monitoring:
            return
        
        self._monitoring = False
        self._stop_event.set()
        
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
        
        self.logger.info("Performance monitoring stopped")
    
    def _monitor_loop(self, interval: float):
        """Main monitoring loop."""
        while not self._stop_event.wait(interval):
            try:
                # Collect system metrics
                system_metrics = self._collect_system_metrics()
                self._system_metrics.append(system_metrics)
                
                # Collect trading metrics
                trading_metrics = self._collect_trading_metrics()
                self._trading_metrics.append(trading_metrics)
                
                # Check for alerts
                self._check_alerts(system_metrics, trading_metrics)
                
                # Log metrics
                self._log_metrics(system_metrics, trading_metrics)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}", exc_info=True)
    
    def _collect_system_metrics(self) -> PerformanceMetrics:
        """Collect system performance metrics."""
        # CPU and memory
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_mb = memory.used / (1024 * 1024)
        
        # Disk I/O
        disk_io = psutil.disk_io_counters()
        if self._last_disk_stats:
            disk_read_mb = (disk_io.read_bytes - self._last_disk_stats.read_bytes) / (1024 * 1024)
            disk_write_mb = (disk_io.write_bytes - self._last_disk_stats.write_bytes) / (1024 * 1024)
        else:
            disk_read_mb = 0.0
            disk_write_mb = 0.0
        self._last_disk_stats = disk_io
        
        # Network I/O
        network_io = psutil.net_io_counters()
        if self._last_network_stats:
            network_sent_mb = (network_io.bytes_sent - self._last_network_stats.bytes_sent) / (1024 * 1024)
            network_recv_mb = (network_io.bytes_recv - self._last_network_stats.bytes_recv) / (1024 * 1024)
        else:
            network_sent_mb = 0.0
            network_recv_mb = 0.0
        self._last_network_stats = network_io
        
        # Process-specific metrics
        process = psutil.Process()
        active_connections = len(process.connections())
        open_files = len(process.open_files())
        thread_count = process.num_threads()
        
        return PerformanceMetrics(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_mb=memory_used_mb,
            disk_io_read_mb=disk_read_mb,
            disk_io_write_mb=disk_write_mb,
            network_sent_mb=network_sent_mb,
            network_recv_mb=network_recv_mb,
            active_connections=active_connections,
            open_files=open_files,
            thread_count=thread_count
        )
    
    def _collect_trading_metrics(self) -> TradingMetrics:
        """Collect trading performance metrics."""
        state = self._trading_state
        
        # Calculate derived metrics
        win_rate = (state['winning_trades'] / state['total_trades']) if state['total_trades'] > 0 else 0.0
        
        # Calculate profit factor
        winning_pnl = sum(pnl for pnl in state['pnl_history'] if pnl > 0)
        losing_pnl = abs(sum(pnl for pnl in state['pnl_history'] if pnl < 0))
        profit_factor = (winning_pnl / losing_pnl) if losing_pnl > 0 else float('inf')
        
        # Calculate Sharpe ratio (simplified)
        if len(state['pnl_history']) > 1:
            pnl_std = statistics.stdev(state['pnl_history'])
            pnl_mean = statistics.mean(state['pnl_history'])
            sharpe_ratio = (pnl_mean / pnl_std) if pnl_std > 0 else 0.0
        else:
            sharpe_ratio = 0.0
        
        # Calculate average trade duration
        avg_trade_duration = (statistics.mean(state['trade_durations']) 
                            if state['trade_durations'] else 0.0)
        
        return TradingMetrics(
            timestamp=datetime.now(),
            total_trades=state['total_trades'],
            winning_trades=state['winning_trades'],
            losing_trades=state['losing_trades'],
            total_pnl=state['total_pnl'],
            unrealized_pnl=state['unrealized_pnl'],
            realized_pnl=state['realized_pnl'],
            max_drawdown=state['max_drawdown'],
            current_drawdown=state['current_drawdown'],
            win_rate=win_rate,
            profit_factor=profit_factor,
            sharpe_ratio=sharpe_ratio,
            avg_trade_duration=avg_trade_duration,
            active_positions=state['active_positions'],
            total_volume=state['total_volume']
        )
    
    def _check_alerts(self, system_metrics: PerformanceMetrics, trading_metrics: TradingMetrics):
        """Check for performance alerts."""
        alerts = []
        
        # System alerts
        system_checks = [
            ('cpu_percent', system_metrics.cpu_percent),
            ('memory_percent', system_metrics.memory_percent),
            ('memory_used_mb', system_metrics.memory_used_mb),
            ('active_connections', system_metrics.active_connections),
            ('open_files', system_metrics.open_files),
            ('thread_count', system_metrics.thread_count),
        ]
        
        for metric_name, current_value in system_checks:
            threshold = self.thresholds.get(metric_name)
            if threshold and current_value > threshold:
                severity = self._get_alert_severity(metric_name, current_value, threshold)
                alert = Alert(
                    timestamp=datetime.now(),
                    alert_type='system',
                    severity=severity,
                    message=f"{metric_name} exceeded threshold: {current_value:.2f} > {threshold:.2f}",
                    metric_name=metric_name,
                    current_value=current_value,
                    threshold_value=threshold
                )
                alerts.append(alert)
        
        # Trading alerts
        trading_checks = [
            ('max_drawdown', trading_metrics.max_drawdown),
            ('current_drawdown', trading_metrics.current_drawdown),
        ]
        
        for metric_name, current_value in trading_checks:
            threshold = self.thresholds.get(metric_name)
            if threshold and current_value > threshold:
                severity = self._get_alert_severity(metric_name, current_value, threshold)
                alert = Alert(
                    timestamp=datetime.now(),
                    alert_type='trading',
                    severity=severity,
                    message=f"{metric_name} exceeded threshold: {current_value:.2f} > {threshold:.2f}",
                    metric_name=metric_name,
                    current_value=current_value,
                    threshold_value=threshold
                )
                alerts.append(alert)
        
        # Add new alerts
        for alert in alerts:
            self._alerts.append(alert)
            self.logger.warning(f"Performance alert: {alert.message}")
            
            # Call alert callback if provided
            if self.alert_callback:
                try:
                    self.alert_callback(alert)
                except Exception as e:
                    self.logger.error(f"Error in alert callback: {e}")
    
    def _get_alert_severity(self, metric_name: str, current_value: float, threshold: float) -> str:
        """Determine alert severity based on how much the threshold is exceeded."""
        ratio = current_value / threshold
        
        if ratio >= 2.0:
            return 'critical'
        elif ratio >= 1.5:
            return 'high'
        elif ratio >= 1.2:
            return 'medium'
        else:
            return 'low'
    
    def _log_metrics(self, system_metrics: PerformanceMetrics, trading_metrics: TradingMetrics):
        """Log performance metrics."""
        # Log to file
        metrics_data = {
            'timestamp': datetime.now().isoformat(),
            'system': asdict(system_metrics),
            'trading': asdict(trading_metrics)
        }
        
        log_file = self.log_dir / "performance_metrics.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(metrics_data, default=str) + '\n')
    
    def update_trading_state(self, **kwargs):
        """Update trading state for metrics calculation."""
        for key, value in kwargs.items():
            if key in self._trading_state:
                self._trading_state[key] = value
    
    def record_trade(self, pnl: float, duration: float, volume: float):
        """Record a completed trade."""
        self._trading_state['total_trades'] += 1
        self._trading_state['total_volume'] += volume
        self._trading_state['trade_durations'].append(duration)
        self._trading_state['pnl_history'].append(pnl)
        
        if pnl > 0:
            self._trading_state['winning_trades'] += 1
        else:
            self._trading_state['losing_trades'] += 1
        
        # Update PnL and drawdown
        self._trading_state['realized_pnl'] += pnl
        self._trading_state['total_pnl'] = self._trading_state['realized_pnl'] + self._trading_state['unrealized_pnl']
        
        # Update peak equity and drawdown
        current_equity = self._trading_state['total_pnl']
        if current_equity > self._trading_state['peak_equity']:
            self._trading_state['peak_equity'] = current_equity
            self._trading_state['current_drawdown'] = 0.0
        else:
            self._trading_state['current_drawdown'] = (self._trading_state['peak_equity'] - current_equity) / self._trading_state['peak_equity']
            self._trading_state['max_drawdown'] = max(self._trading_state['max_drawdown'], self._trading_state['current_drawdown'])
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        if not self._system_metrics or not self._trading_metrics:
            return {}
        
        return {
            'system': asdict(self._system_metrics[-1]),
            'trading': asdict(self._trading_metrics[-1]),
            'alerts': [asdict(alert) for alert in self._alerts[-10:]]  # Last 10 alerts
        }
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter metrics by time
        recent_system_metrics = [m for m in self._system_metrics if m.timestamp >= cutoff_time]
        recent_trading_metrics = [m for m in self._trading_metrics if m.timestamp >= cutoff_time]
        recent_alerts = [a for a in self._alerts if a.timestamp >= cutoff_time]
        
        if not recent_system_metrics or not recent_trading_metrics:
            return {}
        
        # Calculate averages and extremes
        system_summary = {
            'avg_cpu_percent': statistics.mean([m.cpu_percent for m in recent_system_metrics]),
            'max_cpu_percent': max([m.cpu_percent for m in recent_system_metrics]),
            'avg_memory_percent': statistics.mean([m.memory_percent for m in recent_system_metrics]),
            'max_memory_percent': max([m.memory_percent for m in recent_system_metrics]),
            'avg_memory_used_mb': statistics.mean([m.memory_used_mb for m in recent_system_metrics]),
            'max_memory_used_mb': max([m.memory_used_mb for m in recent_system_metrics]),
        }
        
        trading_summary = {
            'total_trades': recent_trading_metrics[-1].total_trades if recent_trading_metrics else 0,
            'win_rate': recent_trading_metrics[-1].win_rate if recent_trading_metrics else 0.0,
            'total_pnl': recent_trading_metrics[-1].total_pnl if recent_trading_metrics else 0.0,
            'max_drawdown': recent_trading_metrics[-1].max_drawdown if recent_trading_metrics else 0.0,
            'current_drawdown': recent_trading_metrics[-1].current_drawdown if recent_trading_metrics else 0.0,
            'profit_factor': recent_trading_metrics[-1].profit_factor if recent_trading_metrics else 0.0,
            'sharpe_ratio': recent_trading_metrics[-1].sharpe_ratio if recent_trading_metrics else 0.0,
        }
        
        alert_summary = {
            'total_alerts': len(recent_alerts),
            'critical_alerts': len([a for a in recent_alerts if a.severity == 'critical']),
            'high_alerts': len([a for a in recent_alerts if a.severity == 'high']),
            'medium_alerts': len([a for a in recent_alerts if a.severity == 'medium']),
            'low_alerts': len([a for a in recent_alerts if a.severity == 'low']),
        }
        
        return {
            'period_hours': hours,
            'system': system_summary,
            'trading': trading_summary,
            'alerts': alert_summary,
            'timestamp': datetime.now().isoformat()
        }
    
    def export_metrics(self, file_path: str, hours: int = 24):
        """Export performance metrics to file."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_system_metrics = [asdict(m) for m in self._system_metrics if m.timestamp >= cutoff_time]
        recent_trading_metrics = [asdict(m) for m in self._trading_metrics if m.timestamp >= cutoff_time]
        recent_alerts = [asdict(a) for a in self._alerts if a.timestamp >= cutoff_time]
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'period_hours': hours,
            'system_metrics': recent_system_metrics,
            'trading_metrics': recent_trading_metrics,
            'alerts': recent_alerts,
            'summary': self.get_performance_summary(hours)
        }
        
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        self.logger.info(f"Performance metrics exported to {file_path}")

# Global performance monitor instance
_performance_monitor: Optional[PerformanceMonitor] = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get or create global performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor

def start_performance_monitoring(interval: float = 5.0):
    """Start global performance monitoring."""
    monitor = get_performance_monitor()
    monitor.start_monitoring(interval)

def stop_performance_monitoring():
    """Stop global performance monitoring."""
    global _performance_monitor
    if _performance_monitor:
        _performance_monitor.stop_monitoring()

if __name__ == "__main__":
    """CLI for performance monitoring."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Performance Monitoring System")
    parser.add_argument("--start", action="store_true", help="Start monitoring")
    parser.add_argument("--stop", action="store_true", help="Stop monitoring")
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--export", help="Export metrics to file")
    parser.add_argument("--hours", type=int, default=24, help="Hours of data to export")
    parser.add_argument("--interval", type=float, default=5.0, help="Monitoring interval")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    monitor = get_performance_monitor()
    
    if args.start:
        monitor.start_monitoring(args.interval)
        print("Performance monitoring started")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            monitor.stop_monitoring()
            print("Performance monitoring stopped")
    
    elif args.stop:
        monitor.stop_monitoring()
        print("Performance monitoring stopped")
    
    elif args.status:
        metrics = monitor.get_current_metrics()
        if metrics:
            print("Current Performance Metrics:")
            print(json.dumps(metrics, indent=2, default=str))
        else:
            print("No metrics available")
    
    elif args.export:
        monitor.export_metrics(args.export, args.hours)
        print(f"Metrics exported to {args.export}")
    
    else:
        parser.print_help()
