"""
Pytest configuration and fixtures for the trading system tests

This module provides common fixtures and configuration for all tests.
"""

import pytest
import sys
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return {
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


@pytest.fixture
def sample_market_data():
    """Sample market data for testing"""
    return [
        {
            "t": 1640995200000 + i * 300000,  # 5-minute intervals
            "o": 2000 + i * 0.5,
            "h": 2010 + i * 0.5,
            "l": 1990 + i * 0.5,
            "c": 2005 + i * 0.5,
            "v": 1000 + i * 10
        }
        for i in range(100)  # 100 data points
    ]


@pytest.fixture
def large_market_data():
    """Large market dataset for performance testing"""
    return [
        {
            "t": 1640995200000 + i * 300000,
            "o": 2000 + i * 0.1,
            "h": 2010 + i * 0.1,
            "l": 1990 + i * 0.1,
            "c": 2005 + i * 0.1,
            "v": 1000 + i
        }
        for i in range(10000)  # 10,000 data points
    ]


@pytest.fixture
def risk_config():
    """Risk management configuration for testing"""
    return {
        "max_position_size": 0.1,
        "max_daily_loss": 0.05,
        "stop_loss_pct": 0.02,
        "take_profit_pct": 0.05,
        "max_leverage": 10,
        "max_positions": 3
    }


@pytest.fixture
def position_config():
    """Position management configuration for testing"""
    return {
        "initial_capital": 10000,
        "max_position_size": 0.1,
        "min_position_size": 0.01
    }


@pytest.fixture
def temp_config_file(sample_config):
    """Temporary configuration file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_config, f)
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    Path(temp_file).unlink(missing_ok=True)


@pytest.fixture
def temp_data_file(sample_market_data):
    """Temporary market data file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_market_data, f)
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    Path(temp_file).unlink(missing_ok=True)


@pytest.fixture
def mock_strategy():
    """Mock strategy for testing"""
    strategy = Mock()
    strategy.name = "MockStrategy"
    strategy.market = "ETH-PERP"
    strategy.timeframe = "5m"
    strategy.compute_indicators.return_value = {
        "rsi": 50.0,
        "current_price": 2000.0,
        "current_volume": 1000.0
    }
    strategy.generate_signal.return_value = Mock(direction="NONE")
    return strategy


@pytest.fixture
def mock_backtester():
    """Mock backtester for testing"""
    backtester = Mock()
    backtester.run_backtest.return_value = {
        "total_trades": 10,
        "winning_trades": 6,
        "losing_trades": 4,
        "win_rate": 0.6,
        "net_profit": 500.0,
        "max_drawdown": 0.05,
        "final_capital": 10500.0
    }
    return backtester


@pytest.fixture
def mock_risk_manager():
    """Mock risk manager for testing"""
    risk_manager = Mock()
    risk_manager.check_position_limit.return_value = True
    risk_manager.check_daily_loss_limit.return_value = False
    risk_manager.check_leverage_limit.return_value = True
    risk_manager.calculate_stop_loss.return_value = 1960.0
    risk_manager.calculate_take_profit.return_value = 2100.0
    return risk_manager


@pytest.fixture
def mock_position_manager():
    """Mock position manager for testing"""
    position_manager = Mock()
    position_manager.calculate_position_size.return_value = 0.05
    position_manager.get_current_positions.return_value = []
    position_manager.add_position.return_value = True
    position_manager.close_position.return_value = True
    return position_manager


@pytest.fixture
def mock_trading_engine():
    """Mock trading engine for testing"""
    engine = Mock()
    engine.is_running = False
    engine.is_paused = False
    engine.start.return_value = True
    engine.stop.return_value = True
    engine.pause.return_value = True
    engine.resume.return_value = True
    return engine


@pytest.fixture
def mock_data_loader():
    """Mock data loader for testing"""
    loader = Mock()
    loader.load_market_data.return_value = [
        {
            "t": 1640995200000,
            "o": 2000.0,
            "h": 2010.0,
            "l": 1990.0,
            "c": 2005.0,
            "v": 1000.0
        }
    ]
    loader.validate_market_data.return_value = True
    loader.validate_price.return_value = True
    loader.validate_timestamp.return_value = True
    return loader


@pytest.fixture
def mock_config_validator():
    """Mock config validator for testing"""
    validator = Mock()
    validator.validate_config.return_value = True
    validator.validate_strategy_params.return_value = True
    validator.validate_trading_params.return_value = True
    return validator


@pytest.fixture
def mock_health_check():
    """Mock health check for testing"""
    def mock_health():
        return {
            "IMPORTS": "PASS",
            "API_CONNECTION": "FAIL",
            "CONFIG": "PASS",
            "STRATEGIES": "PASS",
            "BACKTESTING": "PASS",
            "LIVE_SIMULATION": "PASS",
            "LIVE_TRADING": "FAIL",
            "FILE_SYSTEM": "PASS"
        }
    
    with patch('utils.health_check.health_check', side_effect=mock_health):
        yield mock_health


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment for each test"""
    # Set test environment variables
    import os
    os.environ['TESTING'] = 'true'
    os.environ['LOG_LEVEL'] = 'WARNING'
    
    yield
    
    # Cleanup
    if 'TESTING' in os.environ:
        del os.environ['TESTING']
    if 'LOG_LEVEL' in os.environ:
        del os.environ['LOG_LEVEL']


@pytest.fixture
def sample_trade_data():
    """Sample trade data for testing"""
    return {
        "timestamp": 1640995200000,
        "symbol": "ETH-PERP",
        "side": "LONG",
        "size": 0.1,
        "price": 2000.0,
        "value": 200.0,
        "fee": 0.2,
        "pnl": 10.0
    }


@pytest.fixture
def sample_portfolio_data():
    """Sample portfolio data for testing"""
    return {
        "total_value": 10000.0,
        "available_balance": 9500.0,
        "unrealized_pnl": 500.0,
        "realized_pnl": 200.0,
        "positions": [
            {
                "symbol": "ETH-PERP",
                "side": "LONG",
                "size": 0.1,
                "entry_price": 2000.0,
                "current_price": 2050.0,
                "unrealized_pnl": 50.0
            }
        ]
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest settings"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers"""
    for item in items:
        # Add slow marker to performance tests
        if "performance" in item.nodeid:
            item.add_marker(pytest.mark.slow)
        
        # Add integration marker to integration tests
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Add performance marker to performance tests
        if "test_performance" in item.nodeid:
            item.add_marker(pytest.mark.performance)
