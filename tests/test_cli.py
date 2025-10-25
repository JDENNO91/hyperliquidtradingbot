"""
Tests for CLI functionality

This module tests all command-line interface components.
"""

import pytest
import sys
import subprocess
import tempfile
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestCLICommands:
    """Test CLI command functionality"""
    
    def setup_method(self):
        """Setup test configuration"""
        self.test_config = {
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
                "t": 1640995200000 + i * 60000,
                "o": 100 + i * 0.1,
                "h": 105 + i * 0.1,
                "l": 95 + i * 0.1,
                "c": 102 + i * 0.1,
                "v": 1000 + i * 10
            }
            for i in range(1000)
        ]
    
    def test_backtest_cli_help(self):
        """Test backtest CLI help command"""
        result = subprocess.run([
            sys.executable, "-m", "cli.backtest", "--help"
        ], capture_output=True, text=True, cwd="src")
        
        assert result.returncode == 0
        assert "backtest" in result.stdout.lower()
        assert "config" in result.stdout.lower()
    
    def test_simulate_cli_help(self):
        """Test simulate CLI help command"""
        result = subprocess.run([
            sys.executable, "-m", "cli.simulate", "--help"
        ], capture_output=True, text=True, cwd="src")
        
        assert result.returncode == 0
        assert "simulate" in result.stdout.lower()
        assert "profile" in result.stdout.lower()
    
    def test_trade_cli_help(self):
        """Test trade CLI help command"""
        result = subprocess.run([
            sys.executable, "-m", "cli.trade", "--help"
        ], capture_output=True, text=True, cwd="src")
        
        assert result.returncode == 0
        assert "trade" in result.stdout.lower()
        assert "profile" in result.stdout.lower()
    
    def test_optimize_cli_help(self):
        """Test optimize CLI help command"""
        result = subprocess.run([
            sys.executable, "-m", "cli.optimize", "--help"
        ], capture_output=True, text=True, cwd="src")
        
        assert result.returncode == 0
        assert "optimize" in result.stdout.lower()
        assert "profile" in result.stdout.lower()
    
    def test_backtest_cli_with_config(self):
        """Test backtest CLI with valid config"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as config_file:
            json.dump(self.test_config, config_file)
            config_path = config_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as data_file:
            json.dump(self.mock_data, data_file)
            data_path = data_file.name
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "cli.backtest",
                "--config", config_path,
                "--data", data_path,
                "--log-level", "ERROR"  # Reduce noise
            ], capture_output=True, text=True, cwd="src", timeout=30)
            
            # Should complete successfully
            assert result.returncode == 0
            assert "Backtest completed" in result.stdout or "Processed" in result.stdout
        finally:
            Path(config_path).unlink()
            Path(data_path).unlink()
    
    def test_backtest_cli_invalid_config(self):
        """Test backtest CLI with invalid config"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as config_file:
            json.dump({"invalid": "config"}, config_file)
            config_path = config_file.name
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "cli.backtest",
                "--config", config_path,
                "--log-level", "ERROR"
            ], capture_output=True, text=True, cwd="src", timeout=10)
            
            # Should fail with invalid config
            assert result.returncode != 0
        finally:
            Path(config_path).unlink()
    
    def test_backtest_cli_missing_config(self):
        """Test backtest CLI with missing config file"""
        result = subprocess.run([
            sys.executable, "-m", "cli.backtest",
            "--config", "nonexistent.json",
            "--log-level", "ERROR"
        ], capture_output=True, text=True, cwd="src", timeout=10)
        
        # Should fail with missing config
        assert result.returncode != 0
        assert "not found" in result.stderr.lower() or "error" in result.stderr.lower()


class TestConfigValidation:
    """Test configuration validation"""
    
    def test_valid_config(self):
        """Test valid configuration passes validation"""
        from config.validator import ConfigValidator
        
        valid_config = {
            "strategy": "bbrsi",
            "trading": {
                "market": "ETH-PERP",
                "positionSize": 0.1,
                "leverage": 5,
                "timeframe": "1m"
            },
            "indicators": {
                "rsi": {"period": 14, "overbought": 70, "oversold": 30},
                "bollinger": {"period": 20, "stdDev": 2},
                "adx": {"period": 14, "threshold": 20}
            }
        }
        
        validator = ConfigValidator()
        is_valid, errors = validator.validate(valid_config)
        
        assert is_valid
        assert len(errors) == 0
    
    def test_invalid_config(self):
        """Test invalid configuration fails validation"""
        from config.validator import ConfigValidator
        
        invalid_config = {
            "strategy": "invalid_strategy",
            "trading": {
                "market": "INVALID-MARKET",
                "positionSize": -0.1,  # Invalid negative value
                "leverage": 0,  # Invalid zero leverage
                "timeframe": "invalid"
            }
        }
        
        validator = ConfigValidator()
        is_valid, errors = validator.validate(invalid_config)
        
        assert not is_valid
        assert len(errors) > 0


if __name__ == "__main__":
    pytest.main([__file__])
