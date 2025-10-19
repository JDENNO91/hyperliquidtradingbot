"""
Strategy Factory

This module provides a factory pattern for creating trading strategies based on configuration.
It allows dynamic strategy selection and instantiation.
"""

from typing import Dict, Any, Type
import logging
from core.base_strategy import BaseStrategy

# Import core strategies
from .core.bbrsi_strategy import BBRSIStrategy
from .core.scalping_strategy import ScalpingStrategy
from .core.ma_crossover_rsi_hybrid import MACrossoverRSIHybrid
from .core.rsi_scalping_strategy import RSIScalpingStrategy

# Import timeframe-optimized strategies (legacy - still functional)
from .timeframe_optimized.super_optimized_strategy import SuperOptimizedStrategy
from .timeframe_optimized.super_optimized_5m_strategy import SuperOptimized5mStrategy
from .timeframe_optimized.super_optimized_15m_strategy import SuperOptimized15mStrategy

class StrategyFactory:
    """
    Factory class for creating trading strategies.
    
    This class provides a centralized way to create strategy instances based on
    configuration, making it easy to switch between different strategies or
    create strategies dynamically.
    """
    
    # Registry of available strategies
    _strategies: Dict[str, Type[BaseStrategy]] = {
        # Production strategies (NEW - Highest performing)
        'rsi_scalping': RSIScalpingStrategy,           # 97% return, 2.94% DD (BEST)
        'ma_rsi_hybrid': MACrossoverRSIHybrid,         # 96% return, 3.53% DD, 10% win rate
        
        # Legacy strategies (Original - Still functional)
        'bbrsi': BBRSIStrategy,                         # Original BBRSI
        'scalping': ScalpingStrategy,                   # Original scalping
        
        # Legacy timeframe-optimized strategies (superseded by production strategies)
        'super_optimized': SuperOptimizedStrategy,        # 1m - 1.94% return
        'super_optimized_5m': SuperOptimized5mStrategy,   # 5m - 1.95% return
        'super_optimized_15m': SuperOptimized15mStrategy, # 15m - 2.06% return
    }
    
    @classmethod
    def register_strategy(cls, name: str, strategy_class: Type[BaseStrategy]):
        """
        Register a new strategy class.
        
        Args:
            name: Strategy name/identifier
            strategy_class: Strategy class to register
        """
        cls._strategies[name] = strategy_class
        logging.getLogger(__name__).info(f"Registered strategy: {name}")
    
    @classmethod
    def get_available_strategies(cls) -> list[str]:
        """
        Get list of available strategy names.
        
        Returns:
            List of registered strategy names
        """
        return list(cls._strategies.keys())
    
    @classmethod
    def create_strategy(cls, strategy_name: str, config: Dict[str, Any], 
                       logger: logging.Logger = None) -> BaseStrategy:
        """
        Create a strategy instance.
        
        Args:
            strategy_name: Name of the strategy to create
            config: Configuration dictionary for the strategy
            logger: Optional logger instance
            
        Returns:
            Strategy instance
            
        Raises:
            ValueError: If strategy name is not recognized
        """
        if strategy_name not in cls._strategies:
            available = ', '.join(cls.get_available_strategies())
            raise ValueError(
                f"Unknown strategy: {strategy_name}. "
                f"Available strategies: {available}"
            )
        
        strategy_class = cls._strategies[strategy_name]
        
        try:
            strategy = strategy_class(config, logger)
            logging.getLogger(__name__).info(f"Created strategy: {strategy_name}")
            return strategy
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to create strategy {strategy_name}: {e}")
            raise
    
    @classmethod
    def create_strategy_from_config(cls, config: Dict[str, Any], 
                                   logger: logging.Logger = None) -> BaseStrategy:
        """
        Create a strategy based on configuration.
        
        Args:
            config: Configuration dictionary containing strategy information
            logger: Optional logger instance
            
        Returns:
            Strategy instance
            
        Raises:
            ValueError: If strategy type is not specified or recognized
        """
        # Try to get strategy type from config
        strategy_type = (
            config.get('strategy', {}).get('type') or
            config.get('strategy_type') or
            'bbrsi'  # Default to BBRSI if not specified
        )
        
        return cls.create_strategy(strategy_type, config, logger)
    
    @classmethod
    def validate_strategy_config(cls, strategy_name: str, config: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate configuration for a specific strategy.
        
        Args:
            strategy_name: Name of the strategy to validate
            config: Configuration to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if strategy_name not in cls._strategies:
            return False, [f"Unknown strategy: {strategy_name}"]
        
        strategy_class = cls._strategies[strategy_name]
        
        try:
            # Create a temporary instance to validate config
            temp_strategy = strategy_class(config)
            return temp_strategy.validate_config(), []
        except Exception as e:
            return False, [f"Configuration validation failed: {e}"]
    
    @classmethod
    def get_strategy_info(cls, strategy_name: str) -> Dict[str, Any]:
        """
        Get information about a strategy.
        
        Args:
            strategy_name: Name of the strategy
            
        Returns:
            Dictionary containing strategy information
        """
        if strategy_name not in cls._strategies:
            return {}
        
        strategy_class = cls._strategies[strategy_name]
        
        return {
            'name': strategy_name,
            'class': strategy_class.__name__,
            'module': strategy_class.__module__,
            'description': getattr(strategy_class, '__doc__', 'No description available'),
            'parameters': cls._get_strategy_parameters(strategy_class)
        }
    
    @classmethod
    def _get_strategy_parameters(cls, strategy_class: Type[BaseStrategy]) -> Dict[str, Any]:
        """
        Extract parameter information from a strategy class.
        
        Args:
            strategy_class: Strategy class to analyze
            
        Returns:
            Dictionary containing parameter information
        """
        # This is a simplified implementation
        # In a more sophisticated version, you could use introspection
        # to extract actual parameter information
        
        if strategy_class == BBRSIStrategy:
            return {
                'indicators': ['RSI', 'Bollinger Bands', 'ADX'],
                'timeframes': ['1m', '5m', '15m', '1h'],
                'markets': ['ETH-PERP', 'BTC-PERP'],
                'parameters': {
                    'rsi_period': 'RSI calculation period',
                    'bb_period': 'Bollinger Bands period',
                    'adx_period': 'ADX calculation period',
                    'rsi_overbought': 'RSI overbought threshold',
                    'rsi_oversold': 'RSI oversold threshold'
                }
            }
        elif strategy_class == ScalpingStrategy:
            return {
                'indicators': ['Price action', 'Volume'],
                'timeframes': ['1m', '5m'],
                'markets': ['ETH-PERP', 'BTC-PERP'],
                'parameters': {
                    'entry_threshold': 'Entry signal threshold',
                    'exit_threshold': 'Exit signal threshold',
                    'max_hold_time': 'Maximum position hold time'
                }
            }
        else:
            return {
                'indicators': ['Unknown'],
                'timeframes': ['Unknown'],
                'markets': ['Unknown'],
                'parameters': {}
            }
