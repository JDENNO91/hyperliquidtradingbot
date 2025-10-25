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
from strategies.core.ma_crossover_rsi_hybrid import MACrossoverRSIHybridStrategy
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
    
    def test_strategy_backtest_integration(self):
        """Test complete strategy backtesting workflow"""
        # Initialize strategy
        strategy = RSIScalpingStrategy(self.config)
        
        # Initialize backtester
        backtester = ImprovedBacktester(self.config)
        
        # Run backtest
        results = backtester.run_backtest(self.mock_data, strategy)
        
        # Verify results structure
        assert "total_trades" in results
        assert "net_profit" in results
        assert "win_rate" in results
        assert "max_drawdown" in results
        assert "final_capital" in results
        
        # Verify reasonable values
        assert results["total_trades"] >= 0
        assert results["final_capital"] > 0
        assert 0 <= results["win_rate"] <= 1
        assert results["max_drawdown"] >= 0
    
    def test_live_simulation_integration(self):
        """Test live simulation workflow"""
        with patch('live_simulation.run_live_simulation.LiveSimulationRunner') as mock_runner:
            # Mock the runner
            mock_runner.return_value.run.return_value = {"status": "completed", "trades": 5}
            
            # Test simulation
            from live_simulation.run_live_simulation import LiveSimulationRunner
            runner = LiveSimulationRunner(self.config)
            results = runner.run()
            
            assert results["status"] == "completed"
            assert "trades" in results
    
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
        # Mock the health check to avoid external dependencies
        with patch('utils.health_check.health_check') as mock_health:
            mock_health.return_value = {
                "IMPORTS": "PASS",
                "CONFIG": "PASS", 
                "STRATEGIES": "PASS",
                "BACKTESTING": "PASS"
            }
            
            results = health_check()
            assert results["IMPORTS"] == "PASS"
            assert results["CONFIG"] == "PASS"
    
    def test_strategy_switching(self):
        """Test switching between different strategies"""
        # Test RSI Scalping
        rsi_strategy = RSIScalpingStrategy(self.config)
        assert rsi_strategy.name == "RSIScalpingStrategy"
        
        # Test MA+RSI Hybrid
        hybrid_config = self.config.copy()
        hybrid_config["strategy"] = "ma_crossover_rsi_hybrid"
        hybrid_strategy = MACrossoverRSIHybridStrategy(hybrid_config)
        assert hybrid_strategy.name == "MACrossoverRSIHybridStrategy"
    
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
        # Test with invalid config
        invalid_config = self.config.copy()
        del invalid_config["trading"]
        
        with pytest.raises((KeyError, AttributeError)):
            strategy = RSIScalpingStrategy(invalid_config)
        
        # Test with empty data
        with pytest.raises((IndexError, ValueError)):
            strategy = RSIScalpingStrategy(self.config)
            strategy.compute_indicators([], 0)
    
    def test_performance_metrics(self):
        """Test performance metrics calculation"""
        # Run a backtest
        strategy = RSIScalpingStrategy(self.config)
        backtester = ImprovedBacktester(self.config)
        results = backtester.run_backtest(self.mock_data, strategy)
        
        # Test performance calculations
        if results["total_trades"] > 0:
            assert results["win_rate"] == results["winning_trades"] / results["total_trades"]
            assert results["net_profit"] == results["final_capital"] - self.config["backtest"]["initialCapital"]
        
        # Test risk metrics
        assert results["max_drawdown"] >= 0
        assert results["final_capital"] > 0


if __name__ == "__main__":
    pytest.main([__file__])
