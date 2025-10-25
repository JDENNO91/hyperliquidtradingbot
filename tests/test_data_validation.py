"""
Data validation tests for the trading system

This module tests data integrity and validation including:
- Market data validation
- Configuration validation
- Input sanitization
- Data format verification
"""

import pytest
import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.data_loader import DataLoader
from config.validator import ConfigValidator


class TestDataValidation:
    """Data validation tests"""
    
    def setup_method(self):
        """Setup test data"""
        self.valid_market_data = [
            {
                "t": 1640995200000,
                "o": 2000.0,
                "h": 2010.0,
                "l": 1990.0,
                "c": 2005.0,
                "v": 1000.0
            },
            {
                "t": 1640995500000,
                "o": 2005.0,
                "h": 2015.0,
                "l": 1995.0,
                "c": 2010.0,
                "v": 1100.0
            }
        ]
        
        self.valid_config = {
            "strategy": "rsi_scalping",
            "trading": {
                "market": "ETH-PERP",
                "positionSize": 0.1,
                "leverage": 5,
                "timeframe": "5m"
            },
            "indicators": {
                "rsi": {
                    "period": 14,
                    "overbought": 70,
                    "oversold": 30
                }
            }
        }
    
    def test_market_data_validation(self):
        """Test market data structure validation"""
        data_loader = DataLoader()
        
        # Test valid data
        assert data_loader.validate_market_data(self.valid_market_data)
        
        # Test invalid data structures
        invalid_data_sets = [
            [],  # Empty data
            [{"t": 1640995200000}],  # Missing required fields
            [{"t": "invalid", "o": 2000, "h": 2010, "l": 1990, "c": 2005, "v": 1000}],  # Invalid timestamp
            [{"t": 1640995200000, "o": "invalid", "h": 2010, "l": 1990, "c": 2005, "v": 1000}],  # Invalid price
        ]
        
        for invalid_data in invalid_data_sets:
            assert not data_loader.validate_market_data(invalid_data)
    
    def test_price_data_validation(self):
        """Test price data validation"""
        data_loader = DataLoader()
        
        # Test valid price data
        valid_prices = [2000.0, 2005.0, 2010.0, 1995.0]
        for price in valid_prices:
            assert data_loader.validate_price(price)
        
        # Test invalid price data
        invalid_prices = [-100.0, 0.0, "invalid", None, float('inf'), float('-inf')]
        for price in invalid_prices:
            assert not data_loader.validate_price(price)
    
    def test_timestamp_validation(self):
        """Test timestamp validation"""
        data_loader = DataLoader()
        
        # Test valid timestamps
        valid_timestamps = [
            1640995200000,  # Unix timestamp in milliseconds
            1640995500000,
            1640995800000
        ]
        
        for timestamp in valid_timestamps:
            assert data_loader.validate_timestamp(timestamp)
        
        # Test invalid timestamps
        invalid_timestamps = [
            "invalid",
            1640995200,  # Unix timestamp in seconds (too small)
            9999999999999,  # Future timestamp
            -1,  # Negative timestamp
            0  # Zero timestamp
        ]
        
        for timestamp in invalid_timestamps:
            assert not data_loader.validate_timestamp(timestamp)
    
    def test_volume_validation(self):
        """Test volume data validation"""
        data_loader = DataLoader()
        
        # Test valid volumes
        valid_volumes = [1000.0, 5000.0, 10000.0]
        for volume in valid_volumes:
            assert data_loader.validate_volume(volume)
        
        # Test invalid volumes
        invalid_volumes = [-100.0, 0.0, "invalid", None]
        for volume in invalid_volumes:
            assert not data_loader.validate_volume(volume)
    
    def test_config_validation(self):
        """Test configuration validation"""
        validator = ConfigValidator()
        
        # Test valid config
        assert validator.validate_config(self.valid_config)
        
        # Test invalid configs
        invalid_configs = [
            {},  # Empty config
            {"strategy": "invalid"},  # Invalid strategy
            {"strategy": "rsi_scalping", "trading": {}},  # Missing trading params
            {"strategy": "rsi_scalping", "trading": {"market": "ETH-PERP", "positionSize": -0.1}},  # Negative position size
        ]
        
        for invalid_config in invalid_configs:
            assert not validator.validate_config(invalid_config)
    
    def test_strategy_parameter_validation(self):
        """Test strategy parameter validation"""
        validator = ConfigValidator()
        
        # Test valid strategy parameters
        valid_strategy_params = {
            "rsi": {
                "period": 14,
                "overbought": 70,
                "oversold": 30
            }
        }
        assert validator.validate_strategy_params("rsi_scalping", valid_strategy_params)
        
        # Test invalid strategy parameters
        invalid_strategy_params = [
            {"rsi": {"period": -14}},  # Negative period
            {"rsi": {"overbought": 50}},  # Invalid overbought level
            {"rsi": {"oversold": 80}},  # Invalid oversold level
            {"invalid_indicator": {}}  # Invalid indicator
        ]
        
        for invalid_params in invalid_strategy_params:
            assert not validator.validate_strategy_params("rsi_scalping", invalid_params)
    
    def test_trading_parameter_validation(self):
        """Test trading parameter validation"""
        validator = ConfigValidator()
        
        # Test valid trading parameters
        valid_trading_params = {
            "market": "ETH-PERP",
            "positionSize": 0.1,
            "leverage": 5,
            "timeframe": "5m"
        }
        assert validator.validate_trading_params(valid_trading_params)
        
        # Test invalid trading parameters
        invalid_trading_params = [
            {"market": "INVALID"},  # Invalid market
            {"positionSize": 1.5},  # Position size > 100%
            {"leverage": 0},  # Invalid leverage
            {"timeframe": "invalid"}  # Invalid timeframe
        ]
        
        for invalid_params in invalid_trading_params:
            assert not validator.validate_trading_params(invalid_params)
    
    def test_data_consistency_validation(self):
        """Test data consistency validation"""
        data_loader = DataLoader()
        
        # Test consistent data
        consistent_data = [
            {"t": 1640995200000, "o": 2000, "h": 2010, "l": 1990, "c": 2005, "v": 1000},
            {"t": 1640995500000, "o": 2005, "h": 2015, "l": 1995, "c": 2010, "v": 1100}
        ]
        assert data_loader.validate_data_consistency(consistent_data)
        
        # Test inconsistent data
        inconsistent_data = [
            {"t": 1640995200000, "o": 2000, "h": 1990, "l": 2010, "c": 2005, "v": 1000},  # High < Low
            {"t": 1640995500000, "o": 2005, "h": 2015, "l": 1995, "c": 2010, "v": 1100}
        ]
        assert not data_loader.validate_data_consistency(inconsistent_data)
    
    def test_ohlc_validation(self):
        """Test OHLC data validation"""
        data_loader = DataLoader()
        
        # Test valid OHLC
        valid_ohlc = {
            "o": 2000.0,
            "h": 2010.0,
            "l": 1990.0,
            "c": 2005.0
        }
        assert data_loader.validate_ohlc(valid_ohlc)
        
        # Test invalid OHLC
        invalid_ohlc_sets = [
            {"o": 2000, "h": 1990, "l": 2010, "c": 2005},  # High < Low
            {"o": 2000, "h": 2010, "l": 1990, "c": 2020},  # Close > High
            {"o": 2000, "h": 2010, "l": 1990, "c": 1980},  # Close < Low
        ]
        
        for invalid_ohlc in invalid_ohlc_sets:
            assert not data_loader.validate_ohlc(invalid_ohlc)
    
    def test_data_range_validation(self):
        """Test data range validation"""
        data_loader = DataLoader()
        
        # Test reasonable price ranges
        reasonable_prices = [100.0, 1000.0, 5000.0, 50000.0]
        for price in reasonable_prices:
            assert data_loader.validate_price_range(price)
        
        # Test unreasonable price ranges
        unreasonable_prices = [0.001, 1000000.0, -100.0]
        for price in unreasonable_prices:
            assert not data_loader.validate_price_range(price)
    
    def test_data_completeness_validation(self):
        """Test data completeness validation"""
        data_loader = DataLoader()
        
        # Test complete data
        complete_data = [
            {"t": 1640995200000, "o": 2000, "h": 2010, "l": 1990, "c": 2005, "v": 1000},
            {"t": 1640995500000, "o": 2005, "h": 2015, "l": 1995, "c": 2010, "v": 1100}
        ]
        assert data_loader.validate_data_completeness(complete_data)
        
        # Test incomplete data
        incomplete_data = [
            {"t": 1640995200000, "o": 2000, "h": 2010, "l": 1990, "c": 2005},  # Missing volume
            {"t": 1640995500000, "o": 2005, "h": 2015, "l": 1995, "c": 2010, "v": 1100}
        ]
        assert not data_loader.validate_data_completeness(incomplete_data)
    
    def test_data_type_validation(self):
        """Test data type validation"""
        data_loader = DataLoader()
        
        # Test correct data types
        correct_types = {
            "t": 1640995200000,  # int
            "o": 2000.0,         # float
            "h": 2010.0,         # float
            "l": 1990.0,         # float
            "c": 2005.0,         # float
            "v": 1000.0          # float
        }
        assert data_loader.validate_data_types(correct_types)
        
        # Test incorrect data types
        incorrect_types = {
            "t": "1640995200000",  # string instead of int
            "o": 2000,             # int instead of float
            "h": "2010.0",         # string instead of float
            "l": 1990,             # int instead of float
            "c": 2005,             # int instead of float
            "v": "1000.0"          # string instead of float
        }
        assert not data_loader.validate_data_types(incorrect_types)


if __name__ == "__main__":
    pytest.main([__file__])
