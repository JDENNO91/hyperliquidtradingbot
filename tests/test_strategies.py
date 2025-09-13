"""
Tests for trading strategies

This module tests all trading strategies including BBRSI, Scalping, and Super Optimized strategies.
"""

import pytest
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from strategies.core.bbrsi_strategy import BBRSIStrategy
from strategies.core.scalping_strategy import ScalpingStrategy
from strategies.timeframe_optimized.super_optimized_strategy import SuperOptimizedStrategy
from strategies.timeframe_optimized.super_optimized_5m_strategy import SuperOptimized5mStrategy
from strategies.timeframe_optimized.super_optimized_15m_strategy import SuperOptimized15mStrategy


class TestBBRSIStrategy:
    """Test BBRSI Strategy functionality"""
    
    def setup_method(self):
        """Setup test configuration"""
        self.config = {
            "trading": {
                "market": "ETH-PERP",
                "timeframe": "1m",
                "leverage": 5,
                "positionSize": 0.1
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
            }
        }
        self.strategy = BBRSIStrategy(self.config)
    
    def test_strategy_initialization(self):
        """Test strategy initializes correctly"""
        assert self.strategy.name == "BBRSIStrategy"
        assert self.strategy.market == "ETH-PERP"
        assert self.strategy.timeframe == "1m"
    
    def test_compute_indicators(self):
        """Test indicator computation"""
        # Mock data
        data = [
            {"c": 100, "h": 105, "l": 95, "v": 1000},
            {"c": 102, "h": 107, "l": 97, "v": 1100},
            {"c": 98, "h": 103, "l": 93, "v": 1200},
        ] * 50  # Need enough data for indicators
        
        indicators = self.strategy.compute_indicators(data, len(data) - 1)
        
        assert "rsi" in indicators
        assert "bollinger" in indicators
        assert "adx" in indicators
        
        # Check indicator values are reasonable
        assert 0 <= indicators["rsi"] <= 100
        assert indicators["bollinger"]["upper"] > indicators["bollinger"]["lower"]
        assert indicators["adx"] >= 0
    
    def test_generate_signal(self):
        """Test signal generation"""
        # Mock data with enough history
        data = [{"c": 100 + i, "h": 105 + i, "l": 95 + i, "v": 1000} for i in range(100)]
        
        signal = self.strategy.generate_signal(data, len(data) - 1)
        
        assert signal is not None
        assert hasattr(signal, 'direction')
        assert signal.direction in ['LONG', 'SHORT', 'NONE', 'CLOSE_LONG', 'CLOSE_SHORT']


class TestScalpingStrategy:
    """Test Scalping Strategy functionality"""
    
    def setup_method(self):
        """Setup test configuration"""
        self.config = {
            "trading": {
                "market": "ETH-PERP",
                "timeframe": "1m",
                "leverage": 5,
                "positionSize": 0.05
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
                    "threshold": 25
                }
            }
        }
        self.strategy = ScalpingStrategy(self.config)
    
    def test_strategy_initialization(self):
        """Test strategy initializes correctly"""
        assert self.strategy.name == "ScalpingStrategy"
        assert self.strategy.market == "ETH-PERP"
        assert self.strategy.timeframe == "1m"
    
    def test_compute_indicators(self):
        """Test indicator computation"""
        data = [{"c": 100 + i, "h": 105 + i, "l": 95 + i, "v": 1000} for i in range(100)]
        
        indicators = self.strategy.compute_indicators(data, len(data) - 1)
        
        assert "atr" in indicators
        assert "current_price" in indicators
        assert "current_volume" in indicators


class TestSuperOptimizedStrategy:
    """Test Super Optimized Strategy functionality"""
    
    def setup_method(self):
        """Setup test configuration"""
        self.config = {
            "trading": {
                "market": "ETH-PERP",
                "timeframe": "1m",
                "leverage": 5,
                "positionSize": 0.4
            },
            "indicators": {
                "super_optimized": {
                    "momentum_threshold": 0.0003,
                    "volume_threshold": 1.05,
                    "volatility_threshold": 0.0003,
                    "ensemble_weights": {
                        "momentum": 0.3,
                        "neural_network": 0.25,
                        "ml_features": 0.25,
                        "volume_analysis": 0.2
                    },
                    "threshold": 0.2
                }
            }
        }
        self.strategy = SuperOptimizedStrategy(self.config)
    
    def test_strategy_initialization(self):
        """Test strategy initializes correctly"""
        assert self.strategy.name == "SuperOptimizedStrategy"
        assert self.strategy.market == "ETH-PERP"
        assert self.strategy.timeframe == "1m"
    
    def test_compute_indicators(self):
        """Test indicator computation"""
        data = [{"c": 100 + i, "h": 105 + i, "l": 95 + i, "v": 1000} for i in range(100)]
        
        indicators = self.strategy.compute_indicators(data, len(data) - 1)
        
        assert "acceleration" in indicators
        assert "current_price" in indicators
        assert "market_regime" in indicators
        assert "momentum_10m" in indicators


if __name__ == "__main__":
    pytest.main([__file__])
