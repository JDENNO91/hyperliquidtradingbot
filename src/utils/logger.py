"""
Unified logging utilities for the Hyperliquid Trading Bot.

This module provides consistent logging configuration across all components.
Now enhanced with structured logging and performance monitoring.
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Import enhanced logging system
from .enhanced_logger import (
    setup_enhanced_logging, 
    get_enhanced_logger, 
    log_function_calls, 
    log_async_function_calls,
    EnhancedLogger
)

def setup_logger(
    name: str,
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: Optional[str] = None,
    log_dir: str = "logs",
    use_enhanced: bool = True
) -> logging.Logger:
    """
    Set up a logger with consistent configuration.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        log_format: Optional custom log format
        log_dir: Directory for log files
        use_enhanced: Whether to use enhanced logging system
        
    Returns:
        Configured logger instance
    """
    if use_enhanced:
        # Use enhanced logging system
        enhanced_logger = setup_enhanced_logging(level, log_dir)
        return enhanced_logger.main_logger
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, str(level).upper()))
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Default log format
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, str(level).upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if specified
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
        
        # Add timestamp to log file if it doesn't have extension
        if not log_file.endswith(('.log', '.txt')):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = f"{log_file}_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_path / log_file)
        file_handler.setLevel(getattr(logging, str(level).upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get an existing logger or create a new one with default settings.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

def setup_file_logging(
    logger: logging.Logger,
    log_file: str,
    log_dir: str = "logs",
    level: str = "INFO"
) -> None:
    """
    Add file logging to an existing logger.
    
    Args:
        logger: Existing logger instance
        log_file: Log file name
        log_dir: Directory for log files
        level: Logging level for file handler
    """
    # Ensure log directory exists
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Add timestamp to log file if it doesn't have extension
    if not log_file.endswith(('.log', '.txt')):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"{log_file}_{timestamp}.log"
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create file handler
    file_handler = logging.FileHandler(log_path / log_file)
    file_handler.setLevel(getattr(logging, str(level).upper()))
    file_handler.setFormatter(formatter)
    
    # Add file handler to logger
    logger.addHandler(file_handler)

def setup_rotating_file_logging(
    logger: logging.Logger,
    log_file: str,
    log_dir: str = "logs",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    level: str = "INFO"
) -> None:
    """
    Set up rotating file logging to prevent log files from growing too large.
    
    Args:
        logger: Existing logger instance
        log_file: Log file name
        log_dir: Directory for log files
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        level: Logging level for file handler
    """
    try:
        from logging.handlers import RotatingFileHandler
        
        # Ensure log directory exists
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
        
        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        # Create rotating file handler
        file_handler = RotatingFileHandler(
            log_path / log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(getattr(logging, str(level).upper()))
        file_handler.setFormatter(formatter)
        
        # Add file handler to logger
        logger.addHandler(file_handler)
        
    except ImportError:
        # Fallback to regular file logging if RotatingFileHandler not available
        setup_file_logging(logger, log_file, log_dir, level)

def setup_timed_file_logging(
    logger: logging.Logger,
    log_file: str,
    log_dir: str = "logs",
    when: str = "midnight",
    interval: int = 1,
    backup_count: int = 30,
    level: str = "INFO"
) -> None:
    """
    Set up timed file logging to rotate logs at specific intervals.
    
    Args:
        logger: Existing logger instance
        log_file: Log file name
        log_dir: Directory for log files
        when: When to rotate ('S', 'M', 'H', 'D', 'midnight')
        interval: Interval between rotations
        backup_count: Number of backup files to keep
        level: Logging level for file handler
    """
    try:
        from logging.handlers import TimedRotatingFileHandler
        
        # Ensure log directory exists
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
        
        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        # Create timed rotating file handler
        file_handler = TimedRotatingFileHandler(
            log_path / log_file,
            when=when,
            interval=interval,
            backupCount=backup_count
        )
        file_handler.setLevel(getattr(logging, str(level).upper()))
        file_handler.setFormatter(formatter)
        
        # Add file handler to logger
        logger.addHandler(file_handler)
        
    except ImportError:
        # Fallback to regular file logging if TimedRotatingFileHandler not available
        setup_file_logging(logger, log_file, log_dir, level)

def get_log_level_from_config(config: Dict[str, Any]) -> str:
    """
    Extract log level from configuration dictionary.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Log level string
    """
    # Check various possible locations for log level
    log_level = (
        config.get('logging', {}).get('level') or
        config.get('log_level') or
        config.get('verbosity') or
        'INFO'
    )
    
    # Normalize log level
    log_level = log_level.upper()
    
    # Validate log level
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if log_level not in valid_levels:
        return 'INFO'
    
    return log_level

def setup_logging_from_config(
    name: str,
    config: Dict[str, Any],
    log_dir: str = "logs"
) -> logging.Logger:
    """
    Set up logging based on configuration dictionary.
    
    Args:
        name: Logger name
        config: Configuration dictionary
        log_dir: Directory for log files
        
    Returns:
        Configured logger instance
    """
    # Extract logging configuration
    logging_config = config.get('logging', {})
    
    # Get log level
    level = get_log_level_from_config(config)
    
    # Get log file
    log_file = logging_config.get('file')
    
    # Get log format
    log_format = logging_config.get('format')
    
    # Set up logger
    logger = setup_logger(name, level, log_file, log_format, log_dir)
    
    # Set up additional logging features if specified
    if logging_config.get('rotating', False):
        max_bytes = logging_config.get('max_bytes', 10 * 1024 * 1024)
        backup_count = logging_config.get('backup_count', 5)
        setup_rotating_file_logging(logger, log_file or f"{name}.log", log_dir, max_bytes, backup_count, level)
    
    if logging_config.get('timed', False):
        when = logging_config.get('when', 'midnight')
        interval = logging_config.get('interval', 1)
        backup_count = logging_config.get('backup_count', 30)
        setup_timed_file_logging(logger, log_file or f"{name}.log", log_dir, when, interval, backup_count, level)
    
    return logger
