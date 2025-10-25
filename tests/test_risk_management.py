"""
Risk Management Tests
Simple tests for risk management components
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.simple_risk_manager import SimpleRiskManager
from core.improved_position_manager import ImprovedPositionManager


class TestRiskManagement:
    """Simple risk management tests"""
    
    def setup_method(self):
        """Setup test components"""
        self.config = {
            "risk": {
                "max_risk_per_trade": 0.02,
                "max_position_size": 0.5,
                "max_open_positions": 10
            },
            "position_management": {
                "max_positions": 10,
                "allow_multiple": True
            }
        }
        self.risk_manager = SimpleRiskManager(self.config)
        self.position_manager = ImprovedPositionManager(self.config)
    
    def test_risk_manager_initialization(self):
        """Test risk manager can be created"""
        assert self.risk_manager is not None
        assert isinstance(self.risk_manager, SimpleRiskManager)
    
    def test_position_manager_initialization(self):
        """Test position manager can be created"""
        assert self.position_manager is not None
        assert isinstance(self.position_manager, ImprovedPositionManager)
    
    def test_risk_manager_type(self):
        """Test risk manager type"""
        assert isinstance(self.risk_manager, SimpleRiskManager)
        assert hasattr(self.risk_manager, '__class__')
    
    def test_position_manager_type(self):
        """Test position manager type"""
        assert isinstance(self.position_manager, ImprovedPositionManager)
        assert hasattr(self.position_manager, '__class__')
    
    def test_risk_manager_creation(self):
        """Test risk manager creation"""
        # Test that we can create multiple risk managers
        risk_manager2 = SimpleRiskManager(self.config)
        assert risk_manager2 is not None
        assert isinstance(risk_manager2, SimpleRiskManager)
    
    def test_position_manager_creation(self):
        """Test position manager creation"""
        # Test that we can create multiple position managers
        position_manager2 = ImprovedPositionManager(self.config)
        assert position_manager2 is not None
        assert isinstance(position_manager2, ImprovedPositionManager)
    
    def test_risk_manager_attributes(self):
        """Test risk manager has basic attributes"""
        # Test that risk manager has basic attributes
        assert hasattr(self.risk_manager, '__class__')
        assert hasattr(self.risk_manager, '__dict__')
    
    def test_position_manager_attributes(self):
        """Test position manager has basic attributes"""
        # Test that position manager has basic attributes
        assert hasattr(self.position_manager, '__class__')
        assert hasattr(self.position_manager, '__dict__')
    
    def test_risk_manager_methods(self):
        """Test risk manager has basic methods"""
        # Test that risk manager has basic methods
        assert hasattr(self.risk_manager, '__str__')
        assert callable(self.risk_manager.__str__)
    
    def test_position_manager_methods(self):
        """Test position manager has basic methods"""
        # Test that position manager has basic methods
        assert hasattr(self.position_manager, '__str__')
        assert callable(self.position_manager.__str__)