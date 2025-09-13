#!/usr/bin/env python3
"""
Enhanced Logging System

Provides comprehensive logging across all modules with structured logging,
performance monitoring, and centralized log management.
"""

import logging
import logging.handlers
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
from datetime import datetime
import traceback
import functools
import time
from contextlib import contextmanager

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""
    
    def format(self, record):
        """Format log record as structured JSON."""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread': record.thread,
            'process': record.process
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 
                          'exc_text', 'stack_info']:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)

class PerformanceLogger:
    """Logger for performance metrics and timing."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self._timers: Dict[str, float] = {}
    
    def start_timer(self, operation: str):
        """Start timing an operation."""
        self._timers[operation] = time.time()
        self.logger.debug(f"Started timing: {operation}")
    
    def end_timer(self, operation: str, log_level: int = logging.INFO):
        """End timing an operation and log the duration."""
        if operation in self._timers:
            duration = time.time() - self._timers[operation]
            del self._timers[operation]
            
            self.logger.log(log_level, f"Operation completed: {operation}", 
                          extra={'operation': operation, 'duration_seconds': duration})
            return duration
        else:
            self.logger.warning(f"Timer not found for operation: {operation}")
            return None
    
    @contextmanager
    def time_operation(self, operation: str, log_level: int = logging.INFO):
        """Context manager for timing operations."""
        self.start_timer(operation)
        try:
            yield
        finally:
            self.end_timer(operation, log_level)

class TradingLogger:
    """Specialized logger for trading operations."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_signal(self, signal_type: str, market: str, price: float, 
                   confidence: float, indicators: Dict[str, Any]):
        """Log trading signal generation."""
        self.logger.info(f"Trading signal generated: {signal_type}", extra={
            'signal_type': signal_type,
            'market': market,
            'price': price,
            'confidence': confidence,
            'indicators': indicators,
            'event_type': 'signal'
        })
    
    def log_trade(self, trade_type: str, market: str, side: str, size: float, 
                  price: float, order_id: Optional[str] = None):
        """Log trade execution."""
        self.logger.info(f"Trade executed: {side} {size} {market} at {price}", extra={
            'trade_type': trade_type,
            'market': market,
            'side': side,
            'size': size,
            'price': price,
            'order_id': order_id,
            'event_type': 'trade'
        })
    
    def log_position_update(self, market: str, position_size: float, 
                           unrealized_pnl: float, realized_pnl: float):
        """Log position updates."""
        self.logger.info(f"Position updated: {market} size={position_size} PnL={unrealized_pnl}", extra={
            'market': market,
            'position_size': position_size,
            'unrealized_pnl': unrealized_pnl,
            'realized_pnl': realized_pnl,
            'event_type': 'position'
        })
    
    def log_risk_event(self, event_type: str, market: str, message: str, 
                       severity: str = 'warning'):
        """Log risk management events."""
        log_level = logging.WARNING if severity == 'warning' else logging.ERROR
        self.logger.log(log_level, f"Risk event: {message}", extra={
            'risk_event_type': event_type,
            'market': market,
            'severity': severity,
            'event_type': 'risk'
        })

class EnhancedLogger:
    """Enhanced logger with structured logging and performance monitoring."""
    
    def __init__(self, name: str, log_dir: str = "logs", 
                 console_level: str = "INFO", file_level: str = "DEBUG",
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5):
        """
        Initialize enhanced logger.
        
        Args:
            name: Logger name
            log_dir: Directory for log files
            console_level: Console logging level
            file_level: File logging level
            max_file_size: Maximum log file size in bytes
            backup_count: Number of backup files to keep
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, console_level.upper()))
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler with rotation
        log_file = self.log_dir / f"{name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_file_size, backupCount=backup_count
        )
        file_handler.setLevel(getattr(logging, file_level.upper()))
        file_formatter = StructuredFormatter()
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Error file handler
        error_file = self.log_dir / f"{name}_errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_file, maxBytes=max_file_size, backupCount=backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        self.logger.addHandler(error_handler)
        
        # Performance logger
        self.performance = PerformanceLogger(self.logger)
        
        # Trading logger
        self.trading = TradingLogger(self.logger)
    
    def get_logger(self) -> logging.Logger:
        """Get the underlying logger instance."""
        return self.logger
    
    def log_system_info(self):
        """Log system information."""
        import platform
        import psutil
        
        system_info = {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'disk_usage': psutil.disk_usage('/').percent
        }
        
        self.logger.info("System information", extra={
            'system_info': system_info,
            'event_type': 'system'
        })

def setup_enhanced_logging(name: str, log_dir: str = "logs", 
                          console_level: str = "INFO", file_level: str = "DEBUG") -> EnhancedLogger:
    """
    Setup enhanced logging for a module.
    
    Args:
        name: Logger name (usually __name__)
        log_dir: Directory for log files
        console_level: Console logging level
        file_level: File logging level
        
    Returns:
        EnhancedLogger instance
    """
    return EnhancedLogger(name, log_dir, console_level, file_level)

def log_function_calls(logger: logging.Logger, level: int = logging.DEBUG):
    """Decorator to log function calls."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.log(level, f"Calling {func.__name__}", extra={
                'function': func.__name__,
                'args': str(args)[:200],  # Truncate long args
                'kwargs': str(kwargs)[:200],
                'event_type': 'function_call'
            })
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.log(level, f"Completed {func.__name__}", extra={
                    'function': func.__name__,
                    'duration_seconds': duration,
                    'success': True,
                    'event_type': 'function_completion'
                })
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Failed {func.__name__}: {e}", extra={
                    'function': func.__name__,
                    'duration_seconds': duration,
                    'success': False,
                    'error': str(e),
                    'event_type': 'function_error'
                }, exc_info=True)
                raise
        
        return wrapper
    return decorator

def log_async_function_calls(logger: logging.Logger, level: int = logging.DEBUG):
    """Decorator to log async function calls."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger.log(level, f"Calling async {func.__name__}", extra={
                'function': func.__name__,
                'args': str(args)[:200],
                'kwargs': str(kwargs)[:200],
                'event_type': 'async_function_call'
            })
            
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.log(level, f"Completed async {func.__name__}", extra={
                    'function': func.__name__,
                    'duration_seconds': duration,
                    'success': True,
                    'event_type': 'async_function_completion'
                })
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Failed async {func.__name__}: {e}", extra={
                    'function': func.__name__,
                    'duration_seconds': duration,
                    'success': False,
                    'error': str(e),
                    'event_type': 'async_function_error'
                }, exc_info=True)
                raise
        
        return wrapper
    return decorator

# Global logger instances
_loggers: Dict[str, EnhancedLogger] = {}

def get_enhanced_logger(name: str, log_dir: str = "logs") -> EnhancedLogger:
    """
    Get or create an enhanced logger instance.
    
    Args:
        name: Logger name
        log_dir: Directory for log files
        
    Returns:
        EnhancedLogger instance
    """
    if name not in _loggers:
        _loggers[name] = EnhancedLogger(name, log_dir)
    return _loggers[name]

def cleanup_logs(log_dir: str = "logs", days_to_keep: int = 30):
    """
    Clean up old log files.
    
    Args:
        log_dir: Directory containing log files
        days_to_keep: Number of days to keep log files
    """
    log_path = Path(log_dir)
    if not log_path.exists():
        return
    
    cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
    
    for log_file in log_path.glob("*.log*"):
        if log_file.stat().st_mtime < cutoff_time:
            log_file.unlink()
            print(f"Deleted old log file: {log_file}")

if __name__ == "__main__":
    """CLI for log management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Logging System")
    parser.add_argument("--cleanup", action="store_true", help="Clean up old log files")
    parser.add_argument("--days", type=int, default=30, help="Days to keep log files")
    parser.add_argument("--test", action="store_true", help="Test logging system")
    
    args = parser.parse_args()
    
    if args.cleanup:
        cleanup_logs(days_to_keep=args.days)
        print(f"Cleaned up log files older than {args.days} days")
    
    if args.test:
        # Test the logging system
        logger = get_enhanced_logger("test_logger")
        
        logger.logger.info("Testing enhanced logging system")
        logger.logger.warning("This is a warning message")
        logger.logger.error("This is an error message")
        
        # Test performance logging
        with logger.performance.time_operation("test_operation"):
            time.sleep(0.1)
        
        # Test trading logging
        logger.trading.log_signal("LONG", "ETH-PERP", 4500.0, 0.8, {"rsi": 30, "bb": "lower"})
        logger.trading.log_trade("MARKET", "ETH-PERP", "LONG", 0.1, 4500.0)
        
        print("Logging test completed. Check logs/ directory for output.")
