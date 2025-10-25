"""
Simple Risk Manager for Live Simulation

This is a simplified risk manager that only handles simulated trading.
No complex live mode logic, just basic drawdown monitoring.
"""

import logging
import time

class SimpleRiskManager:
    """Simple risk manager for live simulation."""
    
    def __init__(self, initial_balance: float, max_drawdown: float = 0.25):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.peak_balance = initial_balance
        self.max_drawdown = max_drawdown
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"Simple risk manager initialized with ${initial_balance:,.2f} initial balance")
        self.logger.info(f"Max drawdown threshold: {max_drawdown*100:.1f}%")
    
    def update_balance(self, new_balance: float):
        """Update the current balance and track peak."""
        self.current_balance = new_balance
        if new_balance > self.peak_balance:
            self.peak_balance = new_balance
        
        # Calculate current drawdown
        drawdown = (self.peak_balance - self.current_balance) / self.peak_balance
        
        self.logger.info(f"Balance: ${self.current_balance:,.2f}, Peak: ${self.peak_balance:,.2f}, Drawdown: {drawdown*100:.2f}%")
        
        # Check if max drawdown exceeded
        if drawdown >= self.max_drawdown:
            self.logger.warning(f"Max drawdown exceeded: {drawdown*100:.2f}% >= {self.max_drawdown*100:.1f}%")
            return True  # Signal to close positions
        
        return False
    
    def get_current_balance(self) -> float:
        """Get current balance."""
        return self.current_balance
    
    def get_peak_balance(self) -> float:
        """Get peak balance."""
        return self.peak_balance
    
    def get_drawdown(self) -> float:
        """Get current drawdown percentage."""
        if self.peak_balance == 0:
            return 0.0
        return (self.peak_balance - self.current_balance) / self.peak_balance
