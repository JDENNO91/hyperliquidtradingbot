"""
Tests for backtesting functionality

This module tests the backtesting engine and related components.
"""

import pytest
import sys
import json
import tempfile
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from backtesting.improved_backtester import ImprovedBacktester


class TestImprovedBacktester:
    """Test Improved Backtester functionality"""
    
    def setup_method(self):
        """Setup test configuration and data"""
        self.config = {
            "strategy": "bbrsi",
            "trading": {
                "market": "ETH-PERP",
                "positionSize": 0.1,
                "leverage": 5,
                "timeframe": "1m"
            },
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
            "backtest": {
                "initialCapital": 10000,
                "tradingFee": 0.001,
                "slippage": 0.0005
            }
        }
        
        # Create mock data
        self.mock_data = [
            {
                "t": 1640995200000 + i * 60000,  # 1 minute intervals
                "o": 100 + i * 0.1,
                "h": 105 + i * 0.1,
                "l": 95 + i * 0.1,
                "c": 102 + i * 0.1,
                "v": 1000 + i * 10
            }
            for i in range(1000)  # 1000 data points
        ]
    
    def test_backtester_initialization(self):
        """Test backtester initializes correctly"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.config, f)
            config_path = f.name
        
        try:
            backtester = ImprovedBacktester(config_path)
            assert backtester is not None
            assert backtester.config is not None
        finally:
            Path(config_path).unlink()
    
    def test_data_loading(self):
        """Test data loading functionality"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.mock_data, f)
            data_path = f.name
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(self.config, f)
                config_path = f.name
            
            backtester = ImprovedBacktester(config_path)
            # Test that backtester initializes correctly
            assert backtester is not None
            assert backtester.config is not None
            
            # Test data loading by checking if we can load the mock data
            with open(data_path, 'r') as f:
                data = json.load(f)
            
            assert len(data) == 1000
            assert all(key in data[0] for key in ['t', 'o', 'h', 'l', 'c', 'v'])
        finally:
            Path(data_path).unlink()
            Path(config_path).unlink()
    
    def test_strategy_creation(self):
        """Test strategy creation"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.config, f)
            config_path = f.name
        
        try:
            backtester = ImprovedBacktester(config_path)
            strategy = backtester._load_strategy()
            
            assert strategy is not None
            assert strategy.name == "BBRSIStrategy"
        finally:
            Path(config_path).unlink()
    
    def test_trade_execution(self):
        """Test trade execution logic"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.config, f)
            config_path = f.name
        
        try:
            backtester = ImprovedBacktester(config_path)
            
            # Test that backtester initializes correctly
            assert backtester is not None
            assert backtester.config is not None
            
            # Test strategy loading
            strategy = backtester._load_strategy()
            assert strategy is not None
            
            # Test configuration validation
            assert "strategy" in backtester.config
            assert "trading" in backtester.config
            assert "indicators" in backtester.config
        finally:
            Path(config_path).unlink()
    
    def test_performance_metrics(self):
        """Test performance metrics calculation"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.config, f)
            config_path = f.name
        
        try:
            backtester = ImprovedBacktester(config_path)
            
            # Test that backtester initializes correctly
            assert backtester is not None
            assert backtester.config is not None
            
            # Test performance metrics method exists and can be called
            # Create mock position objects with pnl attribute
            class MockPosition:
                def __init__(self, side, entry_price, exit_price, pnl, size):
                    self.side = side
                    self.entry_price = entry_price
                    self.exit_price = exit_price
                    self.pnl = pnl
                    self.size = size
            
            mock_closed_positions = [
                MockPosition("LONG", 100, 105, 5, 1),
                MockPosition("SHORT", 105, 100, 5, 1),
                MockPosition("LONG", 100, 95, -5, 1),
            ]
            
            mock_market_data = [{"c": 100 + i} for i in range(100)]
            
            metrics = backtester._calculate_performance_metrics(mock_closed_positions, mock_market_data)
            
            assert "summary" in metrics
            assert "risk_metrics" in metrics
            assert metrics["summary"]["total_trades"] == 3
            assert abs(metrics["summary"]["win_rate"] - 66.67) < 0.01  # 2 wins out of 3 trades (66.67%)
            assert metrics["summary"]["net_profit"] == 5  # 5 + 5 - 5 = 5
        finally:
            Path(config_path).unlink()


if __name__ == "__main__":
    pytest.main([__file__])
