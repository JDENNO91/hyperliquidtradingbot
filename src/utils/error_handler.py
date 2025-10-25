"""
Comprehensive Error Handling System

This module provides robust error handling, recovery mechanisms, and
graceful degradation for the trading system.
"""

import logging
import traceback
import sys
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from enum import Enum
import time
import functools
from contextlib import contextmanager


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorContext:
    """Context information for error handling."""
    component: str
    operation: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    trade_id: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


class TradingError(Exception):
    """Base exception for trading system errors."""
    
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 context: Optional[ErrorContext] = None, recoverable: bool = True):
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.context = context
        self.recoverable = recoverable
        self.timestamp = time.time()


class DataError(TradingError):
    """Data-related errors."""
    pass


class StrategyError(TradingError):
    """Strategy execution errors."""
    pass


class RiskError(TradingError):
    """Risk management errors."""
    pass


class NetworkError(TradingError):
    """Network and API errors."""
    pass


class ConfigurationError(TradingError):
    """Configuration errors."""
    pass


class ErrorHandler:
    """Main error handling system."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.error_counts: Dict[str, int] = {}
        self.recovery_strategies: Dict[str, Callable] = {}
        self.circuit_breakers: Dict[str, bool] = {}
        self.max_errors_per_component = 10
        
        # Setup default recovery strategies
        self._setup_default_recovery_strategies()
    
    def _setup_default_recovery_strategies(self):
        """Setup default recovery strategies for common errors."""
        self.recovery_strategies.update({
            'network_error': self._recover_network_error,
            'data_error': self._recover_data_error,
            'strategy_error': self._recover_strategy_error,
            'risk_error': self._recover_risk_error
        })
    
    def handle_error(self, error: Exception, context: Optional[ErrorContext] = None) -> bool:
        """
        Handle an error with appropriate recovery strategies.
        
        Args:
            error: The exception to handle
            context: Additional context information
            
        Returns:
            bool: True if error was handled successfully, False otherwise
        """
        error_type = type(error).__name__
        component = context.component if context else 'unknown'
        
        # Log the error
        self._log_error(error, context)
        
        # Update error counts
        error_key = f"{component}:{error_type}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Check circuit breaker
        if self._is_circuit_breaker_open(component):
            self.logger.warning(f"Circuit breaker open for component: {component}")
            return False
        
        # Attempt recovery
        if isinstance(error, TradingError) and error.recoverable:
            return self._attempt_recovery(error, context)
        
        # Check if we should open circuit breaker
        if self.error_counts[error_key] >= self.max_errors_per_component:
            self._open_circuit_breaker(component)
            return False
        
        return False
    
    def _log_error(self, error: Exception, context: Optional[ErrorContext]):
        """Log error with appropriate level based on severity."""
        error_msg = f"Error in {context.component if context else 'unknown'}: {str(error)}"
        
        if isinstance(error, TradingError):
            if error.severity == ErrorSeverity.CRITICAL:
                self.logger.critical(error_msg, exc_info=True)
            elif error.severity == ErrorSeverity.HIGH:
                self.logger.error(error_msg, exc_info=True)
            elif error.severity == ErrorSeverity.MEDIUM:
                self.logger.warning(error_msg)
            else:
                self.logger.info(error_msg)
        else:
            self.logger.error(error_msg, exc_info=True)
    
    def _attempt_recovery(self, error: TradingError, context: Optional[ErrorContext]) -> bool:
        """Attempt to recover from an error."""
        error_type = type(error).__name__.lower()
        
        if error_type in self.recovery_strategies:
            try:
                return self.recovery_strategies[error_type](error, context)
            except Exception as recovery_error:
                self.logger.error(f"Recovery failed: {recovery_error}")
                return False
        
        return False
    
    def _recover_network_error(self, error: TradingError, context: Optional[ErrorContext]) -> bool:
        """Recovery strategy for network errors."""
        self.logger.info("Attempting network error recovery...")
        time.sleep(1)  # Brief delay before retry
        return True
    
    def _recover_data_error(self, error: TradingError, context: Optional[ErrorContext]) -> bool:
        """Recovery strategy for data errors."""
        self.logger.info("Attempting data error recovery...")
        # Could implement data validation or fallback data sources
        return True
    
    def _recover_strategy_error(self, error: TradingError, context: Optional[ErrorContext]) -> bool:
        """Recovery strategy for strategy errors."""
        self.logger.info("Attempting strategy error recovery...")
        # Could implement strategy fallback or parameter adjustment
        return True
    
    def _recover_risk_error(self, error: TradingError, context: Optional[ErrorContext]) -> bool:
        """Recovery strategy for risk management errors."""
        self.logger.warning("Risk error - implementing safety measures...")
        # Risk errors should generally not be recovered from automatically
        return False
    
    def _is_circuit_breaker_open(self, component: str) -> bool:
        """Check if circuit breaker is open for a component."""
        return self.circuit_breakers.get(component, False)
    
    def _open_circuit_breaker(self, component: str):
        """Open circuit breaker for a component."""
        self.circuit_breakers[component] = True
        self.logger.critical(f"Circuit breaker opened for component: {component}")
    
    def reset_circuit_breaker(self, component: str):
        """Reset circuit breaker for a component."""
        self.circuit_breakers[component] = False
        self.logger.info(f"Circuit breaker reset for component: {component}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of error counts and circuit breaker status."""
        return {
            'error_counts': self.error_counts.copy(),
            'circuit_breakers': self.circuit_breakers.copy(),
            'total_errors': sum(self.error_counts.values())
        }


def error_handler(component: str, operation: str, 
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 recoverable: bool = True):
    """
    Decorator for automatic error handling.
    
    Args:
        component: Component name for error context
        operation: Operation name for error context
        severity: Default severity for errors
        recoverable: Whether errors are recoverable by default
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            handler = ErrorHandler()
            context = ErrorContext(component=component, operation=operation)
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if not isinstance(e, TradingError):
                    e = TradingError(str(e), severity, context, recoverable)
                
                success = handler.handle_error(e, context)
                if not success:
                    raise e
                
                return None
        
        return wrapper
    return decorator


@contextmanager
def error_context(component: str, operation: str):
    """Context manager for error handling."""
    handler = ErrorHandler()
    context = ErrorContext(component=component, operation=operation)
    
    try:
        yield handler, context
    except Exception as e:
        if not isinstance(e, TradingError):
            e = TradingError(str(e), ErrorSeverity.MEDIUM, context)
        
        handler.handle_error(e, context)
        raise


def safe_execute(func: Callable, *args, **kwargs) -> Optional[Any]:
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Function result or None if error occurred
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        handler = ErrorHandler()
        context = ErrorContext(
            component='safe_execute',
            operation=func.__name__
        )
        handler.handle_error(e, context)
        return None


class RetryMechanism:
    """Retry mechanism for failed operations."""
    
    def __init__(self, max_retries: int = 3, delay: float = 1.0, 
                 backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.delay = delay
        self.backoff_factor = backoff_factor
    
    def retry(self, func: Callable, *args, **kwargs) -> Optional[Any]:
        """
        Retry a function with exponential backoff.
        
        Args:
            func: Function to retry
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or None if all retries failed
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = self.delay * (self.backoff_factor ** attempt)
                    time.sleep(delay)
                else:
                    break
        
        # Log final failure
        handler = ErrorHandler()
        context = ErrorContext(
            component='retry_mechanism',
            operation=func.__name__
        )
        handler.handle_error(last_exception, context)
        
        return None


# Global error handler instance
_global_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get global error handler instance."""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler


def setup_global_error_handling():
    """Setup global error handling."""
    global _global_error_handler
    _global_error_handler = ErrorHandler()
    
    # Setup global exception handler
    def global_exception_handler(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        handler = get_error_handler()
        context = ErrorContext(
            component='global',
            operation='unhandled_exception'
        )
        handler.handle_error(exc_value, context)
    
    sys.excepthook = global_exception_handler


if __name__ == "__main__":
    # Example usage
    setup_global_error_handling()
    
    @error_handler("test", "example_function")
    def example_function(x: int) -> int:
        if x < 0:
            raise TradingError("Negative value not allowed", ErrorSeverity.HIGH)
        return x * 2
    
    # Test error handling
    result = example_function(5)
    print(f"Result: {result}")
    
    # Test error recovery
    result = example_function(-1)
    print(f"Result after error: {result}")
    
    # Test retry mechanism
    retry = RetryMechanism(max_retries=3)
    
    def flaky_function():
        import random
        if random.random() < 0.7:
            raise NetworkError("Network timeout")
        return "Success"
    
    result = retry.retry(flaky_function)
    print(f"Retry result: {result}")
