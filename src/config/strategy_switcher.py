"""
Strategy Switcher - Easy strategy switching system

This module provides a simple way to switch between different trading strategies
with unified configuration management.
"""

import json
import logging
from typing import Dict, Any, List
from pathlib import Path


class StrategySwitcher:
    """
    Strategy Switcher for easy strategy management and switching.
    
    This class provides a unified interface for managing different trading strategies,
    making it easy to switch between them and maintain consistent configurations.
    """
    
    def __init__(self, config_dir: str = "src/config"):
        """
        Initialize the strategy switcher.
        
        Args:
            config_dir: Directory containing strategy configurations
        """
        self.config_dir = Path(config_dir)
        self.logger = logging.getLogger(__name__)
        
        # Available strategies with their configurations
        self.strategies = {
            'bbrsi': {
                'name': 'BBRSI Strategy',
                'description': 'Bollinger Bands + RSI + ADX mean reversion strategy',
                'config_file': 'backtest_eth.json',
                'type': 'bbrsi',
                'timeframe': '1m',
                'risk_level': 'medium',
                'suitable_for': ['ETH-PERP', 'BTC-PERP'],
                'characteristics': {
                    'entry_frequency': 'medium',
                    'hold_time': 'medium',
                    'risk_reward': 'balanced',
                    'market_conditions': 'trending_and_ranging'
                }
            },
            'scalping': {
                'name': 'Scalping Strategy',
                'description': 'High-frequency price action scalping strategy',
                'config_file': 'backtest_scalping_eth.json',
                'type': 'scalping',
                'timeframe': '1m',
                'risk_level': 'high',
                'suitable_for': ['ETH-PERP', 'BTC-PERP'],
                'characteristics': {
                    'entry_frequency': 'high',
                    'hold_time': 'short',
                    'risk_reward': 'tight',
                    'market_conditions': 'volatile'
                }
            }
        }
    
    def get_available_strategies(self) -> List[Dict[str, Any]]:
        """
        Get list of available strategies with their information.
        
        Returns:
            List of strategy information dictionaries
        """
        return [
            {
                'id': strategy_id,
                'name': info['name'],
                'description': info['description'],
                'risk_level': info['risk_level'],
                'characteristics': info['characteristics']
            }
            for strategy_id, info in self.strategies.items()
        ]
    
    def get_strategy_config(self, strategy_id: str, custom_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get configuration for a specific strategy.
        
        Args:
            strategy_id: Strategy identifier ('bbrsi' or 'scalping')
            custom_params: Optional custom parameters to override defaults
            
        Returns:
            Complete strategy configuration dictionary
            
        Raises:
            ValueError: If strategy_id is not recognized
        """
        if strategy_id not in self.strategies:
            available = ', '.join(self.strategies.keys())
            raise ValueError(f"Unknown strategy: {strategy_id}. Available: {available}")
        
        strategy_info = self.strategies[strategy_id]
        config_file = self.config_dir / strategy_info['config_file']
        
        # Load base configuration
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            # Create default configuration if file doesn't exist
            config = self._create_default_config(strategy_id)
        
        # Apply custom parameters if provided
        if custom_params:
            config = self._merge_config(config, custom_params)
        
        # Ensure strategy type is set correctly
        config['strategy'] = strategy_info['type']
        
        return config
    
    def _create_default_config(self, strategy_id: str) -> Dict[str, Any]:
        """
        Create default configuration for a strategy.
        
        Args:
            strategy_id: Strategy identifier
            
        Returns:
            Default configuration dictionary
        """
        base_config = {
            "symbol": "ETH-PERP",
            "timeframe": "1m",
            "data_file": "src/backtesting/data/ETH-PERP/ETH-PERP-1m.json",
            "initial_capital": 10000,
            "max_position_size": 0.1,
            "risk_per_trade": 0.02,
            "max_drawdown": 0.1,
            "start_date": "2024-12-04",
            "end_date": "2024-12-05",
            "commission": 0.0005,
            "slippage": 0.0001,
            "log_level": "WARNING"
        }
        
        if strategy_id == 'bbrsi':
            base_config.update({
                "indicators": {
                    "rsi": {
                        "period": 14,
                        "overbought": 70,
                        "oversold": 30
                    },
                    "bollinger": {
                        "period": 20,
                        "stdDev": 2
                    },
                    "adx": {
                        "period": 14,
                        "threshold": 20
                    }
                },
                "trading": {
                    "positionSize": 0.1,
                    "leverage": 5,
                    "stop_loss_pct": 0.015,
                    "take_profit_pct": 0.03
                }
            })
        elif strategy_id == 'scalping':
            base_config.update({
                "trading": {
                    "entry_threshold": 0.002,
                    "exit_threshold": 0.005,
                    "max_hold_time": 300,
                    "volume_multiplier": 1.5,
                    "stop_loss_pct": 0.003,
                    "max_position_size": 0.05
                }
            })
        
        return base_config
    
    def _merge_config(self, base_config: Dict[str, Any], custom_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge custom parameters into base configuration.
        
        Args:
            base_config: Base configuration dictionary
            custom_params: Custom parameters to merge
            
        Returns:
            Merged configuration dictionary
        """
        config = base_config.copy()
        
        for key, value in custom_params.items():
            if isinstance(value, dict) and key in config and isinstance(config[key], dict):
                config[key].update(value)
            else:
                config[key] = value
        
        return config
    
    def create_backtest_config(self, strategy_id: str, **kwargs) -> Dict[str, Any]:
        """
        Create a backtest configuration for a strategy.
        
        Args:
            strategy_id: Strategy identifier
            **kwargs: Additional configuration parameters
            
        Returns:
            Backtest configuration dictionary
        """
        config = self.get_strategy_config(strategy_id)
        
        # Override with any provided parameters
        for key, value in kwargs.items():
            if key in config:
                config[key] = value
        
        return config
    
    def create_live_config(self, strategy_id: str, **kwargs) -> Dict[str, Any]:
        """
        Create a live trading configuration for a strategy.
        
        Args:
            strategy_id: Strategy identifier
            **kwargs: Additional configuration parameters
            
        Returns:
            Live trading configuration dictionary
        """
        config = self.get_strategy_config(strategy_id)
        
        # Add live trading specific settings
        config.update({
            "mode": "live",
            "api_key": "your_api_key_here",
            "api_secret": "your_api_secret_here",
            "testnet": True,  # Start with testnet
            "max_positions": 1,
            "position_management": {
                "max_concurrent_positions": 1,
                "position_sizing": "fixed",
                "risk_per_trade": 0.02
            }
        })
        
        # Override with any provided parameters
        for key, value in kwargs.items():
            if key in config:
                config[key] = value
        
        return config
    
    def save_config(self, strategy_id: str, config: Dict[str, Any], filename: str = None) -> str:
        """
        Save configuration to file.
        
        Args:
            strategy_id: Strategy identifier
            config: Configuration dictionary
            filename: Optional custom filename
            
        Returns:
            Path to saved configuration file
        """
        if filename is None:
            filename = f"{strategy_id}_config.json"
        
        config_path = self.config_dir / filename
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.logger.info(f"Configuration saved to {config_path}")
        return str(config_path)
    
    def compare_strategies(self, strategy_ids: List[str] = None) -> Dict[str, Any]:
        """
        Compare multiple strategies.
        
        Args:
            strategy_ids: List of strategy IDs to compare (default: all)
            
        Returns:
            Comparison dictionary
        """
        if strategy_ids is None:
            strategy_ids = list(self.strategies.keys())
        
        comparison = {}
        
        for strategy_id in strategy_ids:
            if strategy_id in self.strategies:
                strategy_info = self.strategies[strategy_id]
                comparison[strategy_id] = {
                    'name': strategy_info['name'],
                    'description': strategy_info['description'],
                    'risk_level': strategy_info['risk_level'],
                    'characteristics': strategy_info['characteristics'],
                    'suitable_for': strategy_info['suitable_for']
                }
        
        return comparison
    
    def get_strategy_recommendation(self, market_conditions: str, risk_tolerance: str) -> str:
        """
        Get strategy recommendation based on market conditions and risk tolerance.
        
        Args:
            market_conditions: 'trending', 'ranging', 'volatile', 'low_volatility'
            risk_tolerance: 'low', 'medium', 'high'
            
        Returns:
            Recommended strategy ID
        """
        recommendations = {
            ('trending', 'low'): 'bbrsi',
            ('trending', 'medium'): 'bbrsi',
            ('trending', 'high'): 'scalping',
            ('ranging', 'low'): 'bbrsi',
            ('ranging', 'medium'): 'bbrsi',
            ('ranging', 'high'): 'scalping',
            ('volatile', 'low'): 'bbrsi',
            ('volatile', 'medium'): 'scalping',
            ('volatile', 'high'): 'scalping',
            ('low_volatility', 'low'): 'bbrsi',
            ('low_volatility', 'medium'): 'bbrsi',
            ('low_volatility', 'high'): 'bbrsi'
        }
        
        return recommendations.get((market_conditions, risk_tolerance), 'bbrsi')


# Convenience functions for easy strategy switching
def get_bbrsi_config(**kwargs) -> Dict[str, Any]:
    """Get BBRSI strategy configuration."""
    switcher = StrategySwitcher()
    return switcher.get_strategy_config('bbrsi', kwargs)


def get_scalping_config(**kwargs) -> Dict[str, Any]:
    """Get Scalping strategy configuration."""
    switcher = StrategySwitcher()
    return switcher.get_strategy_config('scalping', kwargs)


def switch_to_strategy(strategy_id: str, **kwargs) -> Dict[str, Any]:
    """
    Switch to a specific strategy with optional custom parameters.
    
    Args:
        strategy_id: Strategy identifier ('bbrsi' or 'scalping')
        **kwargs: Custom configuration parameters
        
    Returns:
        Strategy configuration dictionary
    """
    switcher = StrategySwitcher()
    return switcher.get_strategy_config(strategy_id, kwargs)


if __name__ == "__main__":
    # Example usage
    switcher = StrategySwitcher()
    
    print("Available Strategies:")
    for strategy in switcher.get_available_strategies():
        print(f"- {strategy['id']}: {strategy['name']} ({strategy['risk_level']} risk)")
    
    print("\nStrategy Comparison:")
    comparison = switcher.compare_strategies()
    for strategy_id, info in comparison.items():
        print(f"\n{info['name']}:")
        print(f"  Risk Level: {info['risk_level']}")
        print(f"  Characteristics: {info['characteristics']}")
    
    print("\nRecommendations:")
    print(f"Trending + Medium Risk: {switcher.get_strategy_recommendation('trending', 'medium')}")
    print(f"Volatile + High Risk: {switcher.get_strategy_recommendation('volatile', 'high')}")
