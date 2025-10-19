"""
MA Crossover + RSI Hybrid Strategy

Combines trend-following (MA crossover) with momentum confirmation (RSI).
This is a popular professional approach used by traders to filter false signals.

Theory:
- MA Crossover identifies the trend direction
- RSI confirms momentum and filters out weak signals
- Only enter when BOTH indicators align

Entry Rules:
- LONG: Golden cross (EMA > SMA) AND RSI < 50 (oversold or neutral, room to rise)
- SHORT: Death cross (EMA < SMA) AND RSI > 50 (overbought or neutral, room to fall)

This reduces false signals and improves win rate compared to MA crossover alone.
"""

import logging
from typing import Dict, Any, Optional, List
import numpy as np

from core.base_strategy import BaseStrategy, Signal, Position
from ..indicators.ema import calculate_ema, calculate_sma
from ..indicators.rsi import calculate_rsi

class MACrossoverRSIHybrid(BaseStrategy):
    """
    Hybrid strategy combining MA crossover with RSI confirmation.
    
    Uses MA crossover for trend direction and RSI to confirm momentum,
    filtering out low-probability trades.
    """
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        super().__init__(config, logger)
        
        indicators_config = config.get('indicators', {})
        
        # MA parameters
        self.sma_period = indicators_config.get('sma', {}).get('period', 25)
        self.ema_period = indicators_config.get('ema', {}).get('period', 10)
        
        # RSI parameters
        self.rsi_period = indicators_config.get('rsi', {}).get('period', 14)
        self.rsi_long_threshold = indicators_config.get('rsi', {}).get('long_threshold', 50)
        self.rsi_short_threshold = indicators_config.get('rsi', {}).get('short_threshold', 50)
        
        # Risk management
        trading_config = config.get('trading', {})
        self.position_size = trading_config.get('positionSize', 0.1)
        self.leverage = trading_config.get('leverage', 3)
        self.stop_loss_pct = trading_config.get('stop_loss_pct', 0.03)
        self.take_profit_pct = trading_config.get('take_profit_pct', 0.06)
        
        # Track previous values
        self.prev_ema = None
        self.prev_sma = None
        
        self.logger.info(f"MA+RSI Hybrid initialized: SMA{self.sma_period}/EMA{self.ema_period} + RSI{self.rsi_period}")
    
    def compute_indicators(self, data: List[Dict[str, Any]], index: int) -> Dict[str, Any]:
        """Compute MA and RSI indicators."""
        max_period = max(self.sma_period, self.ema_period, self.rsi_period)
        
        if index < max_period:
            return {}
        
        start_idx = max(0, index - max_period - 10)
        end_idx = index + 1
        closes = [float(candle.get('close', candle.get('c', 0))) for candle in data[start_idx:end_idx]]
        
        if len(closes) < max_period:
            return {}
        
        # Calculate MAs
        sma = calculate_sma(closes, self.sma_period)
        ema_list = calculate_ema(closes, self.ema_period)
        ema = ema_list[-1] if ema_list and ema_list[-1] is not None else 0.0
        
        # Calculate RSI
        rsi = calculate_rsi(closes, self.rsi_period)
        
        # MA difference
        ma_diff_pct = ((ema - sma) / sma) if sma != 0 else 0
        
        return {
            'sma': sma,
            'ema': ema,
            'rsi': rsi,
            'ma_diff_pct': ma_diff_pct,
            'current_price': closes[-1]
        }
    
    def generate_signal(self, data: List[Dict[str, Any]], index: int) -> Signal:
        """Generate signals with MA+RSI confluence."""
        indicators = self.compute_indicators(data, index)
        if not indicators:
            return Signal('NONE', 0.0, 'Insufficient data', {}, 0.0, '', 0.0)
        
        current_ema = indicators['ema']
        current_sma = indicators['sma']
        rsi = indicators['rsi']
        current_price = indicators['current_price']
        
        # Initialize previous values
        if self.prev_ema is None or self.prev_sma is None:
            self.prev_ema = current_ema
            self.prev_sma = current_sma
            return Signal('NONE', 0.0, 'Initializing', {}, 0.0, '', 0.0)
        
        # Detect crossovers
        golden_cross = (self.prev_ema <= self.prev_sma and current_ema > current_sma)
        death_cross = (self.prev_ema >= self.prev_sma and current_ema < current_sma)
        
        prev_ema_temp = self.prev_ema
        prev_sma_temp = self.prev_sma
        self.prev_ema = current_ema
        self.prev_sma = current_sma
        
        # Exit signals
        if self.current_position:
            if self.current_position.side == 'LONG' and death_cross:
                return Signal('CLOSE_LONG', 1.0, 'Death Cross exit', {
                    'ema': current_ema, 'sma': current_sma, 'rsi': rsi
                }, current_price, self.market, data[index].get('timestamp', 0), 0.0)
            
            elif self.current_position.side == 'SHORT' and golden_cross:
                return Signal('CLOSE_SHORT', 1.0, 'Golden Cross exit', {
                    'ema': current_ema, 'sma': current_sma, 'rsi': rsi
                }, current_price, self.market, data[index].get('timestamp', 0), 0.0)
        
        # Entry signals WITH RSI confirmation
        # LONG: Golden cross AND RSI not overbought (room to rise)
        if golden_cross and rsi < self.rsi_long_threshold:
            signal_strength = 0.8 + (0.2 * (self.rsi_long_threshold - rsi) / self.rsi_long_threshold)
            reason = f"LONG: Golden Cross + RSI Confirm (RSI={rsi:.1f} < {self.rsi_long_threshold})"
            stop_loss = current_price * (1 - self.stop_loss_pct)
            
            return Signal('LONG', signal_strength, reason, {
                'ema': current_ema,
                'sma': current_sma,
                'rsi': rsi,
                'ma_diff_pct': indicators['ma_diff_pct'],
                'crossover_type': 'golden_cross_rsi_confirm'
            }, current_price, self.market, data[index].get('timestamp', 0), stop_loss)
        
        # SHORT: Death cross AND RSI not oversold (room to fall)
        elif death_cross and rsi > self.rsi_short_threshold:
            signal_strength = 0.8 + (0.2 * (rsi - self.rsi_short_threshold) / (100 - self.rsi_short_threshold))
            reason = f"SHORT: Death Cross + RSI Confirm (RSI={rsi:.1f} > {self.rsi_short_threshold})"
            stop_loss = current_price * (1 + self.stop_loss_pct)
            
            return Signal('SHORT', signal_strength, reason, {
                'ema': current_ema,
                'sma': current_sma,
                'rsi': rsi,
                'ma_diff_pct': indicators['ma_diff_pct'],
                'crossover_type': 'death_cross_rsi_confirm'
            }, current_price, self.market, data[index].get('timestamp', 0), stop_loss)
        
        # Crossover without RSI confirmation (skip the trade)
        elif golden_cross:
            return Signal('NONE', 0.0, f'Golden Cross but RSI too high (RSI={rsi:.1f})', {
                'rsi': rsi, 'ema': current_ema, 'sma': current_sma
            }, 0.0, '', 0.0)
        
        elif death_cross:
            return Signal('NONE', 0.0, f'Death Cross but RSI too low (RSI={rsi:.1f})', {
                'rsi': rsi, 'ema': current_ema, 'sma': current_sma
            }, 0.0, '', 0.0)
        
        return Signal('NONE', 0.0, f'No crossover (EMA={current_ema:.2f}, SMA={current_sma:.2f}, RSI={rsi:.1f})', {
            'ema': current_ema, 'sma': current_sma, 'rsi': rsi
        }, 0.0, '', 0.0)
    
    def evaluate_position(self, data: List[Dict[str, Any]], index: int) -> Signal:
        """Evaluate positions with profit targets."""
        if not self.current_position:
            return Signal('NONE', 0.0, 'No position', {}, 0.0, '', 0.0)
        
        current_price = float(data[index].get('close', data[index].get('c', 0)))
        entry_price = self.current_position.entry_price
        
        if self.current_position.side == 'LONG':
            profit_pct = (current_price - entry_price) / entry_price
        else:
            profit_pct = (entry_price - current_price) / entry_price
        
        # Take profit
        if profit_pct >= self.take_profit_pct:
            return Signal('CLOSE_ALL', 1.0, f'Take profit: {profit_pct:.2%}',
                        {'profit_pct': profit_pct}, current_price, self.market,
                        data[index].get('timestamp', 0))
        
        # Stop loss
        if profit_pct <= -self.stop_loss_pct:
            return Signal('CLOSE_ALL', 1.0, f'Stop loss: {profit_pct:.2%}',
                        {'profit_pct': profit_pct}, current_price, self.market,
                        data[index].get('timestamp', 0))
        
        return Signal('NONE', 0.0, f'Held (P/L: {profit_pct:.2%})', {}, 0.0, '', 0.0)
    
    def reset_for_backtest(self):
        """Reset for new backtest."""
        self.prev_ema = None
        self.prev_sma = None
    
    def validate_config(self) -> bool:
        """Validate configuration."""
        if not super().validate_config():
            return False
        
        if self.sma_period <= 0 or self.ema_period <= 0:
            self.logger.error("MA periods must be positive")
            return False
        
        if self.rsi_period <= 0:
            self.logger.error("RSI period must be positive")
            return False
        
        return True

