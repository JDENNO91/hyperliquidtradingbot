#!/usr/bin/env python3
"""
Configuration Validation System

Validates configuration files to prevent invalid configs and provide clear error messages.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass

class ConfigValidator:
    """Validates configuration files against schema and business rules."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_config(self, config_path: str) -> Dict[str, Any]:
        """
        Validate a configuration file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Validated configuration dictionary
            
        Raises:
            ConfigValidationError: If validation fails
        """
        self.errors.clear()
        self.warnings.clear()
        
        # Load and parse JSON
        config = self._load_config(config_path)
        
        # Validate structure
        self._validate_structure(config)
        
        # Validate trading parameters
        self._validate_trading_config(config.get('trading', {}))
        
        # Validate indicators
        self._validate_indicators_config(config.get('indicators', {}))
        
        # Validate risk management
        self._validate_risk_config(config.get('risk', {}))
        
        # Validate backtest parameters
        self._validate_backtest_config(config.get('backtest', {}))
        
        # Validate logging configuration
        self._validate_logging_config(config.get('logging', {}))
        
        # Report results
        if self.warnings:
            for warning in self.warnings:
                logger.warning(f"Config warning: {warning}")
        
        if self.errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"- {error}" for error in self.errors)
            raise ConfigValidationError(error_msg)
        
        logger.info(f"Configuration validation passed for {config_path}")
        return config
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load and parse configuration file."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            raise ConfigValidationError(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ConfigValidationError(f"Invalid JSON in configuration file: {e}")
    
    def _validate_structure(self, config: Dict[str, Any]):
        """Validate basic configuration structure."""
        required_sections = ['trading']
        
        for section in required_sections:
            if section not in config:
                self.errors.append(f"Missing required section: {section}")
        
        # Check for unknown sections
        known_sections = {
            'trading', 'indicators', 'risk', 'backtest', 'logging', 
            'position_management', 'database', 'strategy'
        }
        
        for section in config.keys():
            if section not in known_sections:
                self.warnings.append(f"Unknown configuration section: {section}")
    
    def _validate_trading_config(self, trading: Dict[str, Any]):
        """Validate trading configuration."""
        required_fields = ['market', 'timeframe']
        
        for field in required_fields:
            if field not in trading:
                self.errors.append(f"Missing required trading field: {field}")
        
        # Validate market format
        if 'market' in trading:
            market = trading['market']
            if not isinstance(market, str) or not re.match(r'^[A-Z]+-PERP$', market):
                self.errors.append(f"Invalid market format: {market}. Expected format: SYMBOL-PERP")
        
        # Validate timeframe
        if 'timeframe' in trading:
            timeframe = trading['timeframe']
            valid_timeframes = ['1m', '5m', '15m', '1h', '4h', '1d']
            if timeframe not in valid_timeframes:
                self.errors.append(f"Invalid timeframe: {timeframe}. Valid options: {valid_timeframes}")
        
        # Validate leverage
        if 'leverage' in trading:
            leverage = trading['leverage']
            if not isinstance(leverage, (int, float)) or leverage <= 0 or leverage > 100:
                self.errors.append(f"Invalid leverage: {leverage}. Must be between 0 and 100")
        
        # Validate position size
        if 'positionSize' in trading:
            position_size = trading['positionSize']
            if not isinstance(position_size, (int, float)) or position_size <= 0 or position_size > 1:
                self.errors.append(f"Invalid position size: {position_size}. Must be between 0 and 1")
        
        # Validate stop loss and take profit
        for field in ['stop_loss_pct', 'take_profit_pct']:
            if field in trading:
                value = trading[field]
                if not isinstance(value, (int, float)) or value <= 0 or value > 1:
                    self.errors.append(f"Invalid {field}: {value}. Must be between 0 and 1")
    
    def _validate_indicators_config(self, indicators: Dict[str, Any]):
        """Validate indicators configuration."""
        # Validate RSI
        if 'rsi' in indicators:
            rsi = indicators['rsi']
            if 'period' in rsi and (not isinstance(rsi['period'], int) or rsi['period'] <= 0):
                self.errors.append("RSI period must be a positive integer")
            
            if 'overbought' in rsi and (not isinstance(rsi['overbought'], (int, float)) or not 50 <= rsi['overbought'] <= 100):
                self.errors.append("RSI overbought must be between 50 and 100")
            
            if 'oversold' in rsi and (not isinstance(rsi['oversold'], (int, float)) or not 0 <= rsi['oversold'] <= 50):
                self.errors.append("RSI oversold must be between 0 and 50")
        
        # Validate Bollinger Bands
        if 'bollinger' in indicators:
            bb = indicators['bollinger']
            if 'period' in bb and (not isinstance(bb['period'], int) or bb['period'] <= 0):
                self.errors.append("Bollinger Bands period must be a positive integer")
            
            if 'stdDev' in bb and (not isinstance(bb['stdDev'], (int, float)) or bb['stdDev'] <= 0):
                self.errors.append("Bollinger Bands standard deviation must be positive")
        
        # Validate ADX
        if 'adx' in indicators:
            adx = indicators['adx']
            if 'period' in adx and (not isinstance(adx['period'], int) or adx['period'] <= 0):
                self.errors.append("ADX period must be a positive integer")
            
            if 'threshold' in adx and (not isinstance(adx['threshold'], (int, float)) or adx['threshold'] < 0):
                self.errors.append("ADX threshold must be non-negative")
    
    def _validate_risk_config(self, risk: Dict[str, Any]):
        """Validate risk management configuration."""
        # Validate max risk per trade
        if 'max_risk_per_trade' in risk:
            max_risk = risk['max_risk_per_trade']
            if not isinstance(max_risk, (int, float)) or max_risk <= 0 or max_risk > 1:
                self.errors.append("Max risk per trade must be between 0 and 1")
        
        # Validate max position size
        if 'max_position_size' in risk:
            max_pos = risk['max_position_size']
            if not isinstance(max_pos, (int, float)) or max_pos <= 0 or max_pos > 1:
                self.errors.append("Max position size must be between 0 and 1")
        
        # Validate max drawdown
        if 'max_drawdown' in risk:
            max_dd = risk['max_drawdown']
            if not isinstance(max_dd, (int, float)) or max_dd <= 0 or max_dd > 1:
                self.errors.append("Max drawdown must be between 0 and 1")
    
    def _validate_backtest_config(self, backtest: Dict[str, Any]):
        """Validate backtesting configuration."""
        # Validate initial capital
        if 'initialCapital' in backtest:
            capital = backtest['initialCapital']
            if not isinstance(capital, (int, float)) or capital <= 0:
                self.errors.append("Initial capital must be positive")
        
        # Validate trading fee
        if 'tradingFee' in backtest:
            fee = backtest['tradingFee']
            if not isinstance(fee, (int, float)) or fee < 0 or fee > 1:
                self.errors.append("Trading fee must be between 0 and 1")
        
        # Validate slippage
        if 'slippage' in backtest:
            slippage = backtest['slippage']
            if not isinstance(slippage, (int, float)) or slippage < 0 or slippage > 1:
                self.errors.append("Slippage must be between 0 and 1")
        
        # Validate date ranges
        for date_field in ['startDate', 'endDate']:
            if date_field in backtest:
                date_str = backtest[date_field]
                try:
                    datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    self.errors.append(f"Invalid date format for {date_field}: {date_str}. Use YYYY-MM-DD format")
    
    def _validate_logging_config(self, logging_config: Dict[str, Any]):
        """Validate logging configuration."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        
        # Check console logging
        if 'console' in logging_config and 'level' in logging_config['console']:
            level = logging_config['console']['level'].upper()
            if level not in valid_levels:
                self.errors.append(f"Invalid console log level: {level}. Valid options: {valid_levels}")
        
        # Check file logging
        if 'file' in logging_config:
            file_config = logging_config['file']
            if 'level' in file_config:
                level = file_config['level'].upper()
                if level not in valid_levels:
                    self.errors.append(f"Invalid file log level: {level}. Valid options: {valid_levels}")
            
            if 'path' in file_config:
                log_path = file_config['path']
                # Check if log directory exists or can be created
                log_dir = Path(log_path).parent
                if not log_dir.exists():
                    try:
                        log_dir.mkdir(parents=True, exist_ok=True)
                        self.warnings.append(f"Created log directory: {log_dir}")
                    except Exception as e:
                        self.errors.append(f"Cannot create log directory {log_dir}: {e}")

def validate_config_file(config_path: str) -> Dict[str, Any]:
    """
    Convenience function to validate a configuration file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Validated configuration dictionary
        
    Raises:
        ConfigValidationError: If validation fails
    """
    validator = ConfigValidator()
    return validator.validate_config(config_path)

def validate_all_configs(config_dir: str = "src/config") -> Dict[str, Any]:
    """
    Validate all configuration files in a directory.
    
    Args:
        config_dir: Directory containing configuration files
        
    Returns:
        Dictionary mapping config files to validation results
    """
    results = {}
    config_path = Path(config_dir)
    
    if not config_path.exists():
        raise ConfigValidationError(f"Configuration directory not found: {config_dir}")
    
    for config_file in config_path.glob("*.json"):
        try:
            config = validate_config_file(str(config_file))
            results[str(config_file)] = {"status": "valid", "config": config}
            logger.info(f"✅ {config_file.name} - Valid")
        except ConfigValidationError as e:
            results[str(config_file)] = {"status": "invalid", "error": str(e)}
            logger.error(f"❌ {config_file.name} - Invalid: {e}")
    
    return results

if __name__ == "__main__":
    """CLI for configuration validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate configuration files")
    parser.add_argument("config_path", nargs="?", help="Path to configuration file (or directory)")
    parser.add_argument("--all", action="store_true", help="Validate all configs in src/config")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
    
    try:
        if args.all or not args.config_path:
            # Validate all configs
            results = validate_all_configs()
            
            valid_count = sum(1 for r in results.values() if r["status"] == "valid")
            total_count = len(results)
            
            print(f"\n📊 Validation Summary: {valid_count}/{total_count} configs valid")
            
            if valid_count == total_count:
                print("🎉 All configurations are valid!")
            else:
                print("⚠️ Some configurations have issues. Check the logs above.")
                
        else:
            # Validate single config
            config = validate_config_file(args.config_path)
            print(f"✅ Configuration {args.config_path} is valid!")
            
    except ConfigValidationError as e:
        print(f"❌ Validation failed: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        exit(1)
