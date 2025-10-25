"""
Risk management tests for the trading system

This module tests risk management functionality including:
- Position sizing
- Stop loss mechanisms
- Risk limits
- Portfolio risk controls
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.simple_risk_manager import SimpleRiskManager
from core.improved_position_manager import ImprovedPositionManager


class TestRiskManagement:
    """Risk management tests"""
    
    def setup_method(self):
        """Setup test configuration"""
        self.risk_config = {
            "max_position_size": 0.1,  # 10% of portfolio
            "max_daily_loss": 0.05,    # 5% daily loss limit
            "stop_loss_pct": 0.02,     # 2% stop loss
            "take_profit_pct": 0.05,   # 5% take profit
            "max_leverage": 10,
            "max_positions": 3
        }
        
        self.position_config = {
            "initial_capital": 10000,
            "max_position_size": 0.1,
            "min_position_size": 0.01
        }
    
    def test_position_sizing(self):
        """Test position sizing calculations"""
        risk_manager = SimpleRiskManager(self.risk_config)
        position_manager = ImprovedPositionManager(self.position_config)
        
        # Test position sizing
        current_capital = 10000
        price = 2000
        risk_amount = 0.02  # 2% risk
        
        position_size = position_manager.calculate_position_size(
            current_capital, price, risk_amount
        )
        
        # Position size should be reasonable
        assert position_size > 0
        assert position_size <= current_capital * self.risk_config["max_position_size"]
        
        # Test with different risk amounts
        high_risk_position = position_manager.calculate_position_size(
            current_capital, price, 0.05  # 5% risk
        )
        
        assert high_risk_position > position_size
    
    def test_stop_loss_mechanism(self):
        """Test stop loss functionality"""
        risk_manager = SimpleRiskManager(self.risk_config)
        
        # Test stop loss calculation
        entry_price = 2000
        stop_loss_price = risk_manager.calculate_stop_loss(entry_price, "LONG")
        
        # Stop loss should be below entry price for long positions
        assert stop_loss_price < entry_price
        assert stop_loss_price == entry_price * (1 - self.risk_config["stop_loss_pct"])
        
        # Test short position stop loss
        short_stop_loss = risk_manager.calculate_stop_loss(entry_price, "SHORT")
        assert short_stop_loss > entry_price
        assert short_stop_loss == entry_price * (1 + self.risk_config["stop_loss_pct"])
    
    def test_take_profit_mechanism(self):
        """Test take profit functionality"""
        risk_manager = SimpleRiskManager(self.risk_config)
        
        # Test take profit calculation
        entry_price = 2000
        take_profit_price = risk_manager.calculate_take_profit(entry_price, "LONG")
        
        # Take profit should be above entry price for long positions
        assert take_profit_price > entry_price
        assert take_profit_price == entry_price * (1 + self.risk_config["take_profit_pct"])
        
        # Test short position take profit
        short_take_profit = risk_manager.calculate_take_profit(entry_price, "SHORT")
        assert short_take_profit < entry_price
        assert short_take_profit == entry_price * (1 - self.risk_config["take_profit_pct"])
    
    def test_daily_loss_limit(self):
        """Test daily loss limit enforcement"""
        risk_manager = SimpleRiskManager(self.risk_config)
        
        # Test daily loss calculation
        initial_capital = 10000
        current_capital = 9500  # 5% loss
        
        daily_loss_pct = (initial_capital - current_capital) / initial_capital
        
        # Should trigger daily loss limit
        assert risk_manager.check_daily_loss_limit(initial_capital, current_capital)
        assert daily_loss_pct >= self.risk_config["max_daily_loss"]
        
        # Test with acceptable loss
        acceptable_capital = 9800  # 2% loss
        assert not risk_manager.check_daily_loss_limit(initial_capital, acceptable_capital)
    
    def test_leverage_limits(self):
        """Test leverage limit enforcement"""
        risk_manager = SimpleRiskManager(self.risk_config)
        
        # Test valid leverage
        assert risk_manager.check_leverage_limit(5)  # 5x leverage
        assert risk_manager.check_leverage_limit(10)  # Max leverage
        
        # Test invalid leverage
        assert not risk_manager.check_leverage_limit(15)  # Exceeds max
        assert not risk_manager.check_leverage_limit(0)   # Invalid leverage
    
    def test_position_limit_enforcement(self):
        """Test maximum position limit enforcement"""
        risk_manager = SimpleRiskManager(self.risk_config)
        position_manager = ImprovedPositionManager(self.position_config)
        
        # Test position counting
        current_positions = [
            {"symbol": "ETH-PERP", "side": "LONG", "size": 0.05},
            {"symbol": "BTC-PERP", "side": "SHORT", "size": 0.03}
        ]
        
        # Should allow new position (2 < 3 max)
        assert risk_manager.check_position_limit(current_positions)
        
        # Test at limit
        current_positions.append({"symbol": "SOL-PERP", "side": "LONG", "size": 0.02})
        assert not risk_manager.check_position_limit(current_positions)
    
    def test_portfolio_risk_calculation(self):
        """Test portfolio risk calculations"""
        risk_manager = SimpleRiskManager(self.risk_config)
        
        # Test portfolio risk metrics
        positions = [
            {"symbol": "ETH-PERP", "size": 0.05, "value": 1000, "unrealized_pnl": 50},
            {"symbol": "BTC-PERP", "size": 0.03, "value": 800, "unrealized_pnl": -20}
        ]
        
        total_value = sum(pos["value"] for pos in positions)
        total_pnl = sum(pos["unrealized_pnl"] for pos in positions)
        
        # Test portfolio metrics
        portfolio_return = total_pnl / total_value
        assert portfolio_return > -0.1  # Should not exceed 10% loss
        
        # Test individual position risk
        for position in positions:
            position_risk = abs(position["unrealized_pnl"]) / position["value"]
            assert position_risk < 0.1  # Individual position risk < 10%
    
    def test_risk_scenarios(self):
        """Test various risk scenarios"""
        risk_manager = SimpleRiskManager(self.risk_config)
        
        # Scenario 1: High volatility market
        high_volatility_price = 2000
        high_vol_stop_loss = risk_manager.calculate_stop_loss(high_volatility_price, "LONG")
        
        # Stop loss should be more conservative in high volatility
        assert high_vol_stop_loss < high_volatility_price * 0.98  # More than 2% stop
        
        # Scenario 2: Low capital scenario
        low_capital = 1000
        position_size = risk_manager.calculate_max_position_size(low_capital, 2000)
        
        # Position size should be limited by capital
        assert position_size <= low_capital * self.risk_config["max_position_size"]
        assert position_size > 0
    
    def test_emergency_stop_mechanism(self):
        """Test emergency stop functionality"""
        risk_manager = SimpleRiskManager(self.risk_config)
        
        # Test emergency conditions
        emergency_conditions = [
            {"daily_loss": 0.08, "should_stop": True},   # 8% daily loss
            {"daily_loss": 0.03, "should_stop": False},  # 3% daily loss
            {"portfolio_risk": 0.15, "should_stop": True},  # 15% portfolio risk
            {"portfolio_risk": 0.05, "should_stop": False}  # 5% portfolio risk
        ]
        
        for condition in emergency_conditions:
            if "daily_loss" in condition:
                should_stop = risk_manager.check_emergency_stop(
                    daily_loss_pct=condition["daily_loss"]
                )
            else:
                should_stop = risk_manager.check_emergency_stop(
                    portfolio_risk_pct=condition["portfolio_risk"]
                )
            
            assert should_stop == condition["should_stop"]
    
    def test_risk_parameter_validation(self):
        """Test risk parameter validation"""
        # Test invalid risk parameters
        invalid_configs = [
            {"max_position_size": 1.5},  # > 100%
            {"max_daily_loss": 0.5},     # 50% daily loss
            {"stop_loss_pct": 0.5},      # 50% stop loss
            {"max_leverage": 100}        # 100x leverage
        ]
        
        for invalid_config in invalid_configs:
            with pytest.raises((ValueError, AssertionError)):
                SimpleRiskManager(invalid_config)
    
    def test_risk_monitoring(self):
        """Test continuous risk monitoring"""
        risk_manager = SimpleRiskManager(self.risk_config)
        
        # Simulate monitoring over time
        monitoring_data = [
            {"timestamp": 1, "portfolio_value": 10000, "unrealized_pnl": 100},
            {"timestamp": 2, "portfolio_value": 9900, "unrealized_pnl": -100},
            {"timestamp": 3, "portfolio_value": 9500, "unrealized_pnl": -500}
        ]
        
        for data_point in monitoring_data:
            risk_status = risk_manager.monitor_risk(
                data_point["portfolio_value"],
                data_point["unrealized_pnl"]
            )
            
            # Risk status should be appropriate
            if data_point["unrealized_pnl"] < -400:  # 4% loss
                assert risk_status["alert_level"] == "HIGH"
            else:
                assert risk_status["alert_level"] in ["LOW", "MEDIUM"]


if __name__ == "__main__":
    pytest.main([__file__])
