"""
Enhanced Logging System

This module provides comprehensive logging capabilities with structured logging,
performance monitoring, and advanced features for the trading system.
"""

import logging
import logging.handlers
import json
import os
import sys
import functools
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import traceback
import threading
from dataclasses import dataclass, asdict
import colorlog


@dataclass
class LogContext:
    """Context information for structured logging."""
    strategy: str = ""
    market: str = ""
    timeframe: str = ""
    trade_id: str = ""
    session_id: str = ""
    user_id: str = ""
    request_id: str = ""


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""
    
    def format(self, record):
        # Create structured log entry
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
        
        # Add context if available
        if hasattr(record, 'context') and record.context:
            log_entry['context'] = asdict(record.context)
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'getMessage',
                          'context']:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)


class PerformanceLogger:
    """Logger for performance metrics and monitoring."""
    
    def __init__(self, logger_name: str = "performance"):
        self.logger = logging.getLogger(logger_name)
        self.metrics = {}
        self.lock = threading.Lock()
    
    def log_metric(self, metric_name: str, value: float, context: Optional[LogContext] = None):
        """Log a performance metric."""
        with self.lock:
            self.metrics[metric_name] = {
                'value': value,
                'timestamp': datetime.now().isoformat(),
                'context': asdict(context) if context else None
            }
        
        self.logger.info(f"Metric: {metric_name} = {value}", extra={'context': context})
    
    def log_trade_metrics(self, trade_data: Dict[str, Any], context: Optional[LogContext] = None):
        """Log comprehensive trade metrics."""
        metrics = {
            'trade_pnl': trade_data.get('pnl', 0),
            'trade_duration': trade_data.get('duration', 0),
            'entry_price': trade_data.get('entry_price', 0),
            'exit_price': trade_data.get('exit_price', 0),
            'position_size': trade_data.get('size', 0),
            'fees': trade_data.get('fees', 0)
        }
        
        for metric_name, value in metrics.items():
            self.log_metric(metric_name, value, context)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all logged metrics."""
        with self.lock:
            return self.metrics.copy()


class TradingLogger:
    """Specialized logger for trading operations."""
    
    def __init__(self, name: str = "trading"):
        self.logger = logging.getLogger(name)
        self.performance_logger = PerformanceLogger(f"{name}.performance")
    
    def log_signal(self, signal_type: str, market: str, price: float, 
                   confidence: float, context: Optional[LogContext] = None):
        """Log trading signal generation."""
        self.logger.info(
            f"Signal: {signal_type} for {market} at {price} (confidence: {confidence:.2f})",
            extra={'context': context}
        )
    
    def log_trade_execution(self, action: str, market: str, price: float, 
                           size: float, context: Optional[LogContext] = None):
        """Log trade execution."""
        self.logger.info(
            f"Trade: {action} {size} {market} at {price}",
            extra={'context': context}
        )
    
    def log_risk_event(self, event_type: str, message: str, 
                      context: Optional[LogContext] = None):
        """Log risk management events."""
        self.logger.warning(
            f"Risk Event: {event_type} - {message}",
            extra={'context': context}
        )
    
    def log_strategy_switch(self, old_strategy: str, new_strategy: str, 
                           reason: str, context: Optional[LogContext] = None):
        """Log strategy switching events."""
        self.logger.info(
            f"Strategy Switch: {old_strategy} -> {new_strategy} (reason: {reason})",
            extra={'context': context}
        )


class EnhancedLogger:
    """Main enhanced logger class with all features."""
    
    def __init__(self, name: str = "hyperliquid_trading", 
                 log_level: str = "INFO",
                 log_dir: str = "logs"):
        self.name = name
        self.log_level = getattr(logging, log_level.upper())
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Initialize loggers
        self.main_logger = self._setup_main_logger()
        self.trading_logger = TradingLogger(f"{name}.trading")
        self.performance_logger = PerformanceLogger(f"{name}.performance")
        self.error_logger = self._setup_error_logger()
        
        # Context management
        self._context = LogContext()
        self._context_lock = threading.Lock()
    
    def _setup_main_logger(self) -> logging.Logger:
        """Setup the main application logger."""
        logger = logging.getLogger(self.name)
        logger.setLevel(self.log_level)
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white'
            }
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler with structured logging
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / f"{self.name}.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_formatter = StructuredFormatter()
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def _setup_error_logger(self) -> logging.Logger:
        """Setup specialized error logger."""
        error_logger = logging.getLogger(f"{self.name}.error")
        error_logger.setLevel(logging.ERROR)
        
        # Error file handler
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / f"{self.name}_errors.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n%(pathname)s:%(lineno)d'
        )
        error_handler.setFormatter(error_formatter)
        error_logger.addHandler(error_handler)
        
        return error_logger
    
    def set_context(self, **kwargs):
        """Set logging context."""
        with self._context_lock:
            for key, value in kwargs.items():
                if hasattr(self._context, key):
                    setattr(self._context, key, value)
    
    def clear_context(self):
        """Clear logging context."""
        with self._context_lock:
            self._context = LogContext()
    
    def get_context(self) -> LogContext:
        """Get current logging context."""
        with self._context_lock:
            return self._context
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.main_logger.debug(message, extra={'context': self._context, **kwargs})
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.main_logger.info(message, extra={'context': self._context, **kwargs})
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.main_logger.warning(message, extra={'context': self._context, **kwargs})
    
    def error(self, message: str, exc_info: bool = True, **kwargs):
        """Log error message."""
        self.main_logger.error(message, extra={'context': self._context, **kwargs}, exc_info=exc_info)
        self.error_logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = True, **kwargs):
        """Log critical message."""
        self.main_logger.critical(message, extra={'context': self._context, **kwargs}, exc_info=exc_info)
        self.error_logger.critical(message, exc_info=exc_info)
    
    def log_exception(self, message: str = "Exception occurred"):
        """Log current exception with full traceback."""
        self.error(f"{message}: {traceback.format_exc()}")
    
    def log_performance(self, metric_name: str, value: float, **kwargs):
        """Log performance metric."""
        self.performance_logger.log_metric(metric_name, value, self._context)
    
    def log_trade(self, trade_data: Dict[str, Any]):
        """Log trade data."""
        self.trading_logger.log_trade_execution(
            trade_data.get('action', 'UNKNOWN'),
            trade_data.get('market', 'UNKNOWN'),
            trade_data.get('price', 0),
            trade_data.get('size', 0),
            self._context
        )
        self.performance_logger.log_trade_metrics(trade_data, self._context)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get performance metrics summary."""
        return self.performance_logger.get_metrics_summary()


# Global logger instance
_global_logger: Optional[EnhancedLogger] = None


def get_logger(name: str = "hyperliquid_trading") -> EnhancedLogger:
    """Get or create global logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = EnhancedLogger(name)
    return _global_logger


def setup_logging(log_level: str = "INFO", log_dir: str = "logs"):
    """Setup global logging configuration."""
    global _global_logger
    _global_logger = EnhancedLogger(log_level=log_level, log_dir=log_dir)
    return _global_logger


# Convenience functions
def debug(message: str, **kwargs):
    """Log debug message using global logger."""
    get_logger().debug(message, **kwargs)


def info(message: str, **kwargs):
    """Log info message using global logger."""
    get_logger().info(message, **kwargs)


def warning(message: str, **kwargs):
    """Log warning message using global logger."""
    get_logger().warning(message, **kwargs)


def error(message: str, **kwargs):
    """Log error message using global logger."""
    get_logger().error(message, **kwargs)


def critical(message: str, **kwargs):
    """Log critical message using global logger."""
    get_logger().critical(message, **kwargs)


def setup_enhanced_logging(log_level: str = "INFO", log_dir: str = "logs") -> EnhancedLogger:
    """Setup enhanced logging system."""
    return setup_logging(log_level, log_dir)


def get_enhanced_logger(name: str = "hyperliquid_trading") -> EnhancedLogger:
    """Get enhanced logger instance."""
    return get_logger(name)


def get_logger(name: str = "hyperliquid_trading") -> EnhancedLogger:
    """Get or create global logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = EnhancedLogger(name)
    return _global_logger


def log_function_calls(func):
    """Decorator to log function calls."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger()
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed with error: {e}")
            raise
    return wrapper


def log_async_function_calls(func):
    """Decorator to log async function calls."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger = get_logger()
        logger.debug(f"Calling async {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = await func(*args, **kwargs)
            logger.debug(f"Async {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Async {func.__name__} failed with error: {e}")
            raise
    return wrapper


if __name__ == "__main__":
    # Example usage
    logger = setup_logging("DEBUG")
    
    # Set context
    logger.set_context(strategy="BBRSI", market="ETH-PERP", trade_id="12345")
    
    # Log messages
    logger.info("Starting trading session")
    logger.debug("Strategy parameters loaded")
    
    # Log trade
    trade_data = {
        'action': 'BUY',
        'market': 'ETH-PERP',
        'price': 2500.0,
        'size': 0.1,
        'pnl': 25.0,
        'duration': 30
    }
    logger.log_trade(trade_data)
    
    # Log performance metric
    logger.log_performance("sharpe_ratio", 1.85)
    
    # Get metrics summary
    metrics = logger.get_metrics_summary()
    print(f"Metrics: {metrics}")