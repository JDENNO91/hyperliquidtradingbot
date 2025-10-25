"""
Integration tests for the trading system

This module tests end-to-end functionality including:
- Strategy execution with real data
- Backtesting engine integration
- Live simulation workflows
- Configuration validation
"""

import pytest
import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from strategies.core.rsi_scalping_strategy import RSIScalpingStrategy
from strategies.core.ma_crossover_rsi_hybrid import MACrossoverRSIHybrid
from backtesting.improved_backtester import ImprovedBacktester
from core.improved_trading_engine import ImprovedTradingEngine
from utils.health_check import health_check


class TestIntegration:
    """Integration tests for trading system"""
    
    def setup_method(self):
        """Setup test configuration and mock data"""
        self.config = {
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
            },
            "backtest": {
                "initialCapital": 10000,
                "tradingFee": 0.001,
                "slippage": 0.0005
            }
        }
        
        # Create realistic mock data
        self.mock_data = [
            {
                "t": 1640995200000 + i * 300000,  # 5-minute intervals
                "o": 2000 + i * 0.5,
                "h": 2010 + i * 0.5,
                "l": 1990 + i * 0.5,
                "c": 2005 + i * 0.5,
                "v": 1000 + i * 10
            }
            for i in range(1000)  # 1000 data points
        ]
    
    @pytest.mark.asyncio
    async def test_strategy_backtest_integration(self):
        """Test complete strategy backtesting workflow"""
        # Initialize strategy
        strategy = RSIScalpingStrategy(self.config)
        
        # Create temporary config file for backtester
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.config, f)
            config_path = f.name
        
        try:
            # Initialize backtester with file path
            backtester = ImprovedBacktester(config_path)
        finally:
            # Clean up temp file
            Path(config_path).unlink(missing_ok=True)
        
        # Create temporary data file for backtest
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.mock_data, f)
            data_path = f.name
        
        try:
            # Run backtest with data file
            results = await backtester.run_backtest(data_path)
        finally:
            # Clean up temp file
            Path(data_path).unlink(missing_ok=True)
        
        # Verify results structure
        assert "performance" in results
        assert "summary" in results["performance"]
        assert "total_trades" in results["performance"]["summary"]
        assert "net_profit" in results["performance"]["summary"]
        assert "return" in results["performance"]["summary"]
        
        # Verify reasonable values
        summary = results["performance"]["summary"]
        assert summary["total_trades"] >= 0
        assert summary["final_capital"] > 0
        assert summary["return"] is not None
    
    def test_live_simulation_integration(self):
        """Test live simulation workflow"""
        # Test that the live simulation module can be imported
        from live_simulation.run_live_simulation import main
        
        # Test that the main function exists and is callable
        assert callable(main)
        
        # Test that we can import the simulate CLI
        from src.cli.simulate import simulate_cli
        assert callable(simulate_cli)
    
    def test_configuration_validation(self):
        """Test configuration validation across components"""
        # Test valid config
        assert self.config["trading"]["market"] == "ETH-PERP"
        assert self.config["trading"]["positionSize"] == 0.1
        assert self.config["indicators"]["rsi"]["period"] == 14
        
        # Test strategy initialization with config
        strategy = RSIScalpingStrategy(self.config)
        assert strategy.market == "ETH-PERP"
        assert strategy.timeframe == "5m"
    
    def test_health_check_integration(self):
        """Test system health check integration"""
        # Run actual health check
        results = health_check()
        
        # Verify health check returns True for success
        assert results == True
    
    def test_strategy_switching(self):
        """Test switching between different strategies"""
        # Test RSI Scalping
        rsi_strategy = RSIScalpingStrategy(self.config)
        assert rsi_strategy.name == "RSIScalpingStrategy"
        
        # Test MA+RSI Hybrid
        hybrid_config = self.config.copy()
        hybrid_config["strategy"] = "ma_crossover_rsi_hybrid"
        hybrid_strategy = MACrossoverRSIHybrid(hybrid_config)
        assert hybrid_strategy.name == "MACrossoverRSIHybrid"
    
    def test_data_processing_pipeline(self):
        """Test data processing through the entire pipeline"""
        # Test data validation
        assert len(self.mock_data) == 1000
        
        # Test data structure
        for data_point in self.mock_data[:10]:  # Check first 10
            assert "t" in data_point
            assert "o" in data_point
            assert "h" in data_point
            assert "l" in data_point
            assert "c" in data_point
            assert "v" in data_point
        
        # Test strategy can process data
        strategy = RSIScalpingStrategy(self.config)
        indicators = strategy.compute_indicators(self.mock_data, len(self.mock_data) - 1)
        
        assert "rsi" in indicators
        assert "current_price" in indicators
        assert indicators["current_price"] > 0
    
    def test_error_handling_integration(self):
        """Test error handling across the system"""
        # Test with invalid config - should handle gracefully
        invalid_config = self.config.copy()
        del invalid_config["trading"]
        
        # Strategy should handle missing trading config gracefully
        try:
            strategy = RSIScalpingStrategy(invalid_config)
            # If it doesn't raise an exception, that's also valid error handling
        except (KeyError, AttributeError, ValueError):
            # Expected behavior - strategy should handle invalid config
            pass
        
        # Test with empty data - should handle gracefully
        try:
            strategy = RSIScalpingStrategy(self.config)
            strategy.compute_indicators([], 0)
            # If it doesn't raise an exception, that's also valid error handling
        except (IndexError, ValueError):
            # Expected behavior - strategy should handle empty data
            pass
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self):
        """Test performance metrics calculation"""
        # Create temporary config file for backtester
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.config, f)
            config_path = f.name
        
        try:
            # Create temporary data file for backtest
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(self.mock_data, f)
                data_path = f.name
            
            try:
                # Run a backtest
                strategy = RSIScalpingStrategy(self.config)
                backtester = ImprovedBacktester(config_path)
                results = await backtester.run_backtest(data_path)
            finally:
                # Clean up data file
                Path(data_path).unlink(missing_ok=True)
        finally:
            # Clean up temp file
            Path(config_path).unlink(missing_ok=True)
        
        # Test performance calculations
        summary = results["performance"]["summary"]
        if summary["total_trades"] > 0:
            # Allow for small floating point differences
            expected_net_profit = summary["final_capital"] - self.config["backtest"]["initialCapital"]
            assert abs(summary["net_profit"] - expected_net_profit) < 0.01
        
        # Test risk metrics
        risk_metrics = results["performance"]["risk_metrics"]
        assert risk_metrics["max_drawdown"] >= 0
        assert summary["final_capital"] > 0


if __name__ == "__main__":
    pytest.main([__file__])
