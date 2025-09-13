"""
Unified Configuration Manager

This module provides a single, consistent interface for managing all configuration
across backtesting, simulation, and live trading. It consolidates the previous
separate config loaders and provides a clean, hierarchical configuration system.
"""

import json
import os
from typing import Dict, Any, Optional, Union
from pathlib import Path
import logging

from .validator import ConfigValidator, ConfigValidationError

class ConfigManager:
    """
    Unified configuration management system.
    
    This class provides:
    - Hierarchical configuration loading (defaults + profile + overrides)
    - Configuration validation
    - Environment-specific configurations
    - Dynamic configuration updates
    - Configuration export/import
    """
    
    def __init__(self, config_dir: Optional[str] = None, logger: Optional[logging.Logger] = None, 
                 validate_configs: bool = True):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
            logger: Logger instance
            validate_configs: Whether to validate configurations on load
        """
        self.logger = logger or logging.getLogger(__name__)
        self.validate_configs = validate_configs
        
        # Set config directory
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Default to src/config relative to current working directory
            self.config_dir = Path(__file__).parent
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
        
        # Configuration cache
        self._config_cache: Dict[str, Dict[str, Any]] = {}
        self._default_config: Optional[Dict[str, Any]] = None
        
        # Initialize validator if validation is enabled
        if self.validate_configs:
            self.validator = ConfigValidator()
        else:
            self.validator = None
        
        # Load default configuration
        self._load_defaults()
        
        self.logger.info(f"Configuration manager initialized with config directory: {self.config_dir}")
    
    def _load_defaults(self):
        """Load default configuration values."""
        default_path = self.config_dir / "defaults.json"
        
        if default_path.exists():
            try:
                with open(default_path, 'r') as f:
                    self._default_config = json.load(f)
                self.logger.debug("Default configuration loaded")
            except Exception as e:
                self.logger.warning(f"Failed to load default config: {e}")
                self._default_config = {}
        else:
            # Create default configuration if it doesn't exist
            self._default_config = self._create_default_config()
            self._save_defaults()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create a default configuration template."""
        return {
            "trading": {
                "positionSize": 0.1,
                "leverage": 5,
                "leverageMode": "isolated",
                "maxPositions": 20,
                "timeframe": "1m",
                "profitTarget": 1.5,
                "testMode": True,
                "stop_loss_pct": 0.015,
                "take_profit_pct": 0.03,
                "max_consecutive_losses": 3,
                "use_volatility_sizing": True
            },
            "position_management": {
                "max_positions": 20,
                "allow_multiple": True,
                "auto_close_on_loss": False,
                "max_loss_percentage": 0.05
            },
            "indicators": {
                "rsi": {
                    "period": 14,
                    "overbought": 70,
                    "oversold": 30,
                    "extreme_overbought": 75,
                    "extreme_oversold": 25
                },
                "bollinger": {
                    "period": 20,
                    "stdDev": 2
                },
                "adx": {
                    "period": 14,
                    "threshold": 20
                },
                "min_adx_trend": 18,
                "bb_squeeze_threshold": 0.01,
                "volatility_lookback": 20
            },
            "risk": {
                "max_risk_per_trade": 0.02,
                "max_position_size": 0.5,
                "max_open_positions": 20,
                "max_drawdown": 0.25,
                "max_consecutive_losses": 5,
                "volatility_window": 20
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "trading.log"
            }
        }
    
    def _save_defaults(self):
        """Save default configuration to file."""
        default_path = self.config_dir / "defaults.json"
        try:
            with open(default_path, 'w') as f:
                json.dump(self._default_config, f, indent=2)
            self.logger.debug("Default configuration saved")
        except Exception as e:
            self.logger.error(f"Failed to save default config: {e}")
    
    def load_config(self, profile: str, fallback: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration for a specific profile.
        
        Args:
            profile: Configuration profile name (e.g., 'backtest_eth', 'live_btc')
            fallback: Fallback profile if primary profile not found
            
        Returns:
            Merged configuration dictionary
        """
        # Check cache first
        cache_key = f"{profile}_{fallback}" if fallback else profile
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]
        
        # Start with default configuration
        config = self._default_config.copy() if self._default_config else {}
        
        # Load fallback profile if specified
        if fallback:
            fallback_config = self._load_profile(fallback)
            if fallback_config:
                config = self._deep_merge(config, fallback_config)
                self.logger.debug(f"Fallback profile loaded: {fallback}")
        
        # Load primary profile
        primary_config = self._load_profile(profile)
        if primary_config:
            config = self._deep_merge(config, primary_config)
            self.logger.debug(f"Primary profile loaded: {profile}")
        else:
            self.logger.warning(f"Profile not found: {profile}")
        
        # Validate configuration if validator is enabled
        if self.validator:
            try:
                # Create a temporary file for validation
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(config, f, indent=2)
                    temp_path = f.name
                
                # Validate the configuration
                validated_config = self.validator.validate_config(temp_path)
                
                # Clean up temporary file
                os.unlink(temp_path)
                
                # Use validated config
                config = validated_config
                self.logger.debug(f"Configuration validated for profile: {profile}")
                
            except ConfigValidationError as e:
                self.logger.error(f"Configuration validation failed for profile {profile}: {e}")
                raise
            except Exception as e:
                self.logger.warning(f"Configuration validation skipped due to error: {e}")
        
        # Cache the result
        self._config_cache[cache_key] = config
        
        return config
    
    def _load_profile(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """
        Load a specific configuration profile.
        
        Args:
            profile_name: Name of the profile to load
            
        Returns:
            Profile configuration or None if not found
        """
        # Try different file extensions and locations
        possible_paths = [
            self.config_dir / f"{profile_name}.json",
            self.config_dir / "profiles" / f"{profile_name}.json",
            self.config_dir / f"{profile_name}.yaml",
            self.config_dir / "profiles" / f"{profile_name}.yaml"
        ]
        
        for path in possible_paths:
            if path.exists():
                try:
                    with open(path, 'r') as f:
                        if path.suffix == '.json':
                            config = json.load(f)
                        elif path.suffix == '.yaml':
                            import yaml
                            config = yaml.safe_load(f)
                        else:
                            continue
                    
                    self.logger.debug(f"Profile loaded from: {path}")
                    return config
                    
                except Exception as e:
                    self.logger.warning(f"Failed to load profile {profile_name} from {path}: {e}")
        
        return None
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two configuration dictionaries.
        
        Args:
            base: Base configuration
            override: Override configuration
            
        Returns:
            Merged configuration
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def save_profile(self, profile_name: str, config: Dict[str, Any], 
                    profile_dir: Optional[str] = None) -> bool:
        """
        Save a configuration profile.
        
        Args:
            profile_name: Name of the profile
            config: Configuration to save
            profile_dir: Directory to save profile in (defaults to profiles subdirectory)
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            if profile_dir:
                save_dir = Path(profile_dir)
            else:
                save_dir = self.config_dir / "profiles"
            
            save_dir.mkdir(exist_ok=True)
            
            profile_path = save_dir / f"{profile_name}.json"
            
            with open(profile_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.logger.info(f"Profile saved: {profile_path}")
            
            # Clear cache for this profile
            self._clear_cache_for_profile(profile_name)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save profile {profile_name}: {e}")
            return False
    
    def _clear_cache_for_profile(self, profile_name: str):
        """Clear cache entries for a specific profile."""
        keys_to_remove = [key for key in self._config_cache.keys() if profile_name in key]
        for key in keys_to_remove:
            del self._config_cache[key]
    
    def get_available_profiles(self) -> list[str]:
        """
        Get list of available configuration profiles.
        
        Returns:
            List of profile names
        """
        profiles = []
        
        # Check main config directory
        for file_path in self.config_dir.glob("*.json"):
            if file_path.name != "defaults.json":
                profiles.append(file_path.stem)
        
        # Check profiles subdirectory
        profiles_dir = self.config_dir / "profiles"
        if profiles_dir.exists():
            for file_path in profiles_dir.glob("*.json"):
                profiles.append(file_path.stem)
        
        return sorted(profiles)
    
    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate configuration structure and values.
        
        Args:
            config: Configuration to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required sections
        required_sections = ['trading', 'indicators']
        for section in required_sections:
            if section not in config:
                errors.append(f"Missing required section: {section}")
        
        # Validate trading section
        if 'trading' in config:
            trading = config['trading']
            required_trading = ['market', 'positionSize', 'leverage']
            for key in required_trading:
                if key not in trading:
                    errors.append(f"Missing required trading config: {key}")
            
            # Validate numeric values
            if 'positionSize' in trading:
                pos_size = trading['positionSize']
                if not isinstance(pos_size, (int, float)) or pos_size <= 0 or pos_size > 1:
                    errors.append("positionSize must be a number between 0 and 1")
            
            if 'leverage' in trading:
                leverage = trading['leverage']
                if not isinstance(leverage, (int, float)) or leverage <= 0:
                    errors.append("leverage must be a positive number")
        
        # Validate indicators section
        if 'indicators' in config:
            indicators = config['indicators']
            
            # Check RSI configuration
            if 'rsi' in indicators:
                rsi = indicators['rsi']
                if 'period' in rsi and (not isinstance(rsi['period'], int) or rsi['period'] <= 0):
                    errors.append("RSI period must be a positive integer")
                
                if 'overbought' in rsi and (not isinstance(rsi['overbought'], (int, float)) or rsi['overbought'] <= 50):
                    errors.append("RSI overbought must be greater than 50")
                
                if 'oversold' in rsi and (not isinstance(rsi['oversold'], (int, float)) or rsi['oversold'] >= 50):
                    errors.append("RSI oversold must be less than 50")
        
        return len(errors) == 0, errors
    
    def update_config(self, profile_name: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing configuration profile.
        
        Args:
            profile_name: Name of the profile to update
            profile_dir: Directory containing the profile
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            # Load existing config
            existing_config = self.load_config(profile_name)
            
            # Apply updates
            updated_config = self._deep_merge(existing_config, updates)
            
            # Validate updated config
            is_valid, errors = self.validate_config(updated_config)
            if not is_valid:
                self.logger.error(f"Configuration validation failed: {errors}")
                return False
            
            # Save updated config
            return self.save_profile(profile_name, updated_config)
            
        except Exception as e:
            self.logger.error(f"Failed to update profile {profile_name}: {e}")
            return False
    
    def export_config(self, profile_name: str, export_path: str) -> bool:
        """
        Export a configuration profile to a file.
        
        Args:
            profile_name: Name of the profile to export
            export_path: Path to export the configuration to
            
        Returns:
            True if exported successfully, False otherwise
        """
        try:
            config = self.load_config(profile_name)
            
            with open(export_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.logger.info(f"Configuration exported to: {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export profile {profile_name}: {e}")
            return False
    
    def import_config(self, import_path: str, profile_name: str) -> bool:
        """
        Import a configuration from a file.
        
        Args:
            import_path: Path to the configuration file to import
            profile_name: Name to save the imported configuration as
            
        Returns:
            True if imported successfully, False otherwise
        """
        try:
            with open(import_path, 'r') as f:
                config = json.load(f)
            
            # Validate imported config
            is_valid, errors = self.validate_config(config)
            if not is_valid:
                self.logger.error(f"Imported configuration validation failed: {errors}")
                return False
            
            # Save as new profile
            return self.save_profile(profile_name, config)
            
        except Exception as e:
            self.logger.error(f"Failed to import configuration from {import_path}: {e}")
            return False
    
    def clear_cache(self):
        """Clear the configuration cache."""
        self._config_cache.clear()
        self.logger.debug("Configuration cache cleared")
    
    def get_default_config(self) -> Dict[str, Any]:
        """
        Get the default configuration.
        
        Returns:
            Default configuration dictionary
        """
        return self._default_config.copy() if self._default_config else {}
    
    def get_config_summary(self, profile_name: str) -> Dict[str, Any]:
        """
        Get a summary of configuration for a profile.
        
        Args:
            profile_name: Name of the profile
            
        Returns:
            Configuration summary dictionary
        """
        config = self.load_config(profile_name)
        
        summary = {
            'profile': profile_name,
            'trading': {
                'market': config.get('trading', {}).get('market', 'Unknown'),
                'timeframe': config.get('trading', {}).get('timeframe', 'Unknown'),
                'leverage': config.get('trading', {}).get('leverage', 'Unknown'),
                'position_size': config.get('trading', {}).get('positionSize', 'Unknown')
            },
            'indicators': {
                'rsi_period': config.get('indicators', {}).get('rsi', {}).get('period', 'Unknown'),
                'bb_period': config.get('indicators', {}).get('bollinger', {}).get('period', 'Unknown'),
                'adx_period': config.get('indicators', {}).get('adx', {}).get('period', 'Unknown')
            },
            'risk': {
                'max_risk_per_trade': config.get('risk', {}).get('max_risk_per_trade', 'Unknown'),
                'max_drawdown': config.get('risk', {}).get('max_drawdown', 'Unknown')
            }
        }
        
        return summary
