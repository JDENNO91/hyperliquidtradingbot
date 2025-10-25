"""
RSI Scalping Strategy - High Frequency Intraday

Designed for 10+ trades per day using RSI extremes and quick scalps.
Pure momentum strategy without MA crossovers.

Theory:
- Enter on RSI extremes (oversold/overbought)
- Quick profit targets (1-2%)
- Tight stop losses (1%)
- No waiting for crossovers - immediate entries

Entry Rules:
- LONG: RSI < 35 (oversold)
- SHORT: RSI > 65 (overbought)

Exit Rules:
- RSI returns to neutral (45-55)
- Quick profit: +1.5%
- Tight stop: -1%

Target: 10-20 trades per day on 1-5 minute timeframes
"""

import logging
from typing import Dict, Any, Optional, List

from src.core.base_strategy import BaseStrategy, Signal, Position
from ..indicators.rsi import calculate_rsi

class RSIScalpingStrategy(BaseStrategy):
    """
    Pure RSI scalping for high-frequency trading.
    
    Enters on RSI extremes, exits on reversion or profit targets.
    Designed for maximum trade frequency.
    """
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        super().__init__(config, logger)
        
        indicators_config = config.get('indicators', {})
        
        # RSI parameters (aggressive thresholds)
        self.rsi_period = indicators_config.get('rsi', {}).get('period', 14)
        self.rsi_oversold = indicators_config.get('rsi', {}).get('oversold', 35)  # More permissive
        self.rsi_overbought = indicators_config.get('rsi', {}).get('overbought', 65)  # More permissive
        self.rsi_neutral_low = indicators_config.get('rsi', {}).get('neutral_low', 45)
        self.rsi_neutral_high = indicators_config.get('rsi', {}).get('neutral_high', 55)
        
        # Aggressive risk management
        trading_config = config.get('trading', {})
        self.position_size = trading_config.get('positionSize', 0.1)
        self.leverage = trading_config.get('leverage', 5)
        self.stop_loss_pct = trading_config.get('stop_loss_pct', 0.01)  # Tight 1%
        self.take_profit_pct = trading_config.get('take_profit_pct', 0.015)  # Quick 1.5%
        
        # Track previous RSI
        self.prev_rsi = None
        
        self.logger.info(f"RSI Scalping initialized: RSI{self.rsi_period}, Entry:{self.rsi_oversold}/{self.rsi_overbought}")
    
    def compute_indicators(self, data: List[Dict[str, Any]], index: int) -> Dict[str, Any]:
        """Compute RSI."""
        if index < self.rsi_period + 5:
            return {}
        
        start_idx = max(0, index - self.rsi_period - 10)
        end_idx = index + 1
        closes = [float(candle.get('close', candle.get('c', 0))) for candle in data[start_idx:end_idx]]
        
        if len(closes) < self.rsi_period:
            return {}
        
        rsi = calculate_rsi(closes, self.rsi_period)
        
        return {
            'rsi': rsi,
            'current_price': closes[-1]
        }
    
    def generate_signal(self, data: List[Dict[str, Any]], index: int) -> Signal:
        """Generate high-frequency RSI-based signals."""
        indicators = self.compute_indicators(data, index)
        if not indicators:
            return Signal('NONE', 0.0, 'Insufficient data', {}, 0.0, '', 0.0)
        
        rsi = indicators['rsi']
        current_price = indicators['current_price']
        
        # Initialize previous RSI
        if self.prev_rsi is None:
            self.prev_rsi = rsi
            return Signal('NONE', 0.0, 'Initializing', {}, 0.0, '', 0.0)
        
        # Exit signals (RSI returning to neutral)
        if self.current_position:
            if self.current_position.side == 'LONG':
                # Exit LONG when RSI returns to neutral or above
                if rsi >= self.rsi_neutral_low:
                    reason = f"Exit LONG: RSI neutral (RSI={rsi:.1f})"
                    self.prev_rsi = rsi
                    return Signal('CLOSE_LONG', 1.0, reason, {
                        'rsi': rsi, 'exit_type': 'rsi_neutral'
                    }, current_price, self.market, data[index].get('timestamp', 0), 0.0)
            
            elif self.current_position.side == 'SHORT':
                # Exit SHORT when RSI returns to neutral or below
                if rsi <= self.rsi_neutral_high:
                    reason = f"Exit SHORT: RSI neutral (RSI={rsi:.1f})"
                    self.prev_rsi = rsi
                    return Signal('CLOSE_SHORT', 1.0, reason, {
                        'rsi': rsi, 'exit_type': 'rsi_neutral'
                    }, current_price, self.market, data[index].get('timestamp', 0), 0.0)
        
        # Entry signals (RSI extremes)
        # LONG: RSI oversold
        if rsi < self.rsi_oversold and not self.current_position:
            signal_strength = min(1.0, (self.rsi_oversold - rsi) / 20)  # Stronger signal for more extreme RSI
            reason = f"LONG: RSI oversold (RSI={rsi:.1f} < {self.rsi_oversold})"
            stop_loss = current_price * (1 - self.stop_loss_pct)
            
            self.prev_rsi = rsi
            return Signal('LONG', signal_strength, reason, {
                'rsi': rsi,
                'rsi_threshold': self.rsi_oversold,
                'entry_type': 'rsi_oversold'
            }, current_price, self.market, data[index].get('timestamp', 0), stop_loss)
        
        # SHORT: RSI overbought
        elif rsi > self.rsi_overbought and not self.current_position:
            signal_strength = min(1.0, (rsi - self.rsi_overbought) / 20)
            reason = f"SHORT: RSI overbought (RSI={rsi:.1f} > {self.rsi_overbought})"
            stop_loss = current_price * (1 + self.stop_loss_pct)
            
            self.prev_rsi = rsi
            return Signal('SHORT', signal_strength, reason, {
                'rsi': rsi,
                'rsi_threshold': self.rsi_overbought,
                'entry_type': 'rsi_overbought'
            }, current_price, self.market, data[index].get('timestamp', 0), stop_loss)
        
        self.prev_rsi = rsi
        return Signal('NONE', 0.0, f'Waiting for extreme (RSI={rsi:.1f})', {
            'rsi': rsi
        }, 0.0, '', 0.0)
    
    def evaluate_position(self, data: List[Dict[str, Any]], index: int) -> Signal:
        """Evaluate positions with quick profit targets."""
        if not self.current_position:
            return Signal('NONE', 0.0, 'No position', {}, 0.0, '', 0.0)
        
        current_price = float(data[index].get('close', data[index].get('c', 0)))
        entry_price = self.current_position.entry_price
        
        if self.current_position.side == 'LONG':
            profit_pct = (current_price - entry_price) / entry_price
        else:
            profit_pct = (entry_price - current_price) / entry_price
        
        # QUICK profit target (scalping!)
        if profit_pct >= self.take_profit_pct:
            return Signal('CLOSE_ALL', 1.0, f'Quick scalp profit: {profit_pct:.2%}',
                        {'profit_pct': profit_pct}, current_price, self.market,
                        data[index].get('timestamp', 0))
        
        # TIGHT stop loss
        if profit_pct <= -self.stop_loss_pct:
            return Signal('CLOSE_ALL', 1.0, f'Stop loss: {profit_pct:.2%}',
                        {'profit_pct': profit_pct}, current_price, self.market,
                        data[index].get('timestamp', 0))
        
        return Signal('NONE', 0.0, f'Held (P/L: {profit_pct:.2%})', {}, 0.0, '', 0.0)
    
    def reset_for_backtest(self):
        """Reset for new backtest."""
        self.prev_rsi = None
    
    def validate_config(self) -> bool:
        """Validate configuration."""
        if not super().validate_config():
            return False
        
        if self.rsi_period <= 0:
            self.logger.error("RSI period must be positive")
            return False
        
        if self.rsi_oversold >= 50 or self.rsi_overbought <= 50:
            self.logger.error("Invalid RSI thresholds")
            return False
        
        return True

