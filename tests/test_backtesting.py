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
            data = backtester._load_data(data_path)
            
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
            strategy = backtester._create_strategy()
            
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
            
            # Test opening a position
            backtester._open_position("LONG", 100.0, 1.0)
            assert backtester.current_position is not None
            assert backtester.current_position["side"] == "LONG"
            
            # Test closing a position
            backtester._close_position(105.0)
            assert backtester.current_position is None
            assert len(backtester.trades) == 1
            
            trade = backtester.trades[0]
            assert trade["side"] == "LONG"
            assert trade["entry_price"] == 100.0
            assert trade["exit_price"] == 105.0
            assert trade["pnl"] > 0  # Should be profitable
        finally:
            Path(config_path).unlink()
    
    def test_performance_metrics(self):
        """Test performance metrics calculation"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.config, f)
            config_path = f.name
        
        try:
            backtester = ImprovedBacktester(config_path)
            
            # Add some mock trades
            backtester.trades = [
                {"side": "LONG", "entry_price": 100, "exit_price": 105, "pnl": 5, "size": 1},
                {"side": "SHORT", "entry_price": 105, "exit_price": 100, "pnl": 5, "size": 1},
                {"side": "LONG", "entry_price": 100, "exit_price": 95, "pnl": -5, "size": 1},
            ]
            
            metrics = backtester._calculate_performance_metrics()
            
            assert "total_trades" in metrics
            assert "win_rate" in metrics
            assert "total_pnl" in metrics
            assert "max_drawdown" in metrics
            
            assert metrics["total_trades"] == 3
            assert metrics["win_rate"] == 2/3  # 2 wins out of 3 trades
            assert metrics["total_pnl"] == 5  # 5 + 5 - 5 = 5
        finally:
            Path(config_path).unlink()


if __name__ == "__main__":
    pytest.main([__file__])
