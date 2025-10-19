"""
BBRSI Strategy (Bollinger Bands + RSI + ADX)

This strategy combines Bollinger Bands, Relative Strength Index (RSI), and Average Directional Index (ADX)
to identify mean reversion opportunities with trend confirmation.
"""

import logging
from typing import Dict, Any, Optional, List
import numpy as np
from datetime import datetime

from src.core.base_strategy import BaseStrategy, Signal, Position
from ..indicators.rsi import calculate_rsi
from ..indicators.bollinger_bands import calculate_bollinger_bands
from ..indicators.adx import calculate_adx
# Microprice functionality removed - using simpler indicators

class BBRSIStrategy(BaseStrategy):
    """
    BBRSI Strategy Implementation
    
    This strategy looks for:
    1. RSI oversold/overbought conditions
    2. Price near Bollinger Band extremes
    3. ADX trend confirmation
    4. Volatility filtering to avoid low-volatility periods
    
    Entry Conditions:
    - LONG: RSI < oversold, price < lower BB, +DI > -DI, sufficient volatility
    - SHORT: RSI > overbought, price > upper BB, -DI > +DI, sufficient volatility
    
    Exit Conditions:
    - Take profit target reached
    - Stop loss triggered
    - Price returns to middle BB (mean reversion)
    - RSI returns to neutral levels
    """
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        Initialize BBRSI strategy with configuration.
        
        Args:
            config: Strategy configuration dictionary
            logger: Logger instance
        """
        super().__init__(config, logger)
        
        # Extract indicator configuration
        indicators_config = config.get('indicators', {})
        
        # RSI parameters
        self.rsi_period: int = indicators_config.get('rsi', {}).get('period', 14)
        self.rsi_overbought: float = indicators_config.get('rsi', {}).get('overbought', 70)
        self.rsi_oversold: float = indicators_config.get('rsi', {}).get('oversold', 30)
        
        # New RSI thresholds for better signal quality
        self.rsi_extreme_overbought: float = indicators_config.get('rsi', {}).get('extreme_overbought', 72)
        self.rsi_extreme_oversold: float = indicators_config.get('rsi', {}).get('extreme_oversold', 28)
        
        # Bollinger Bands parameters
        self.bb_period: int = indicators_config.get('bollinger', {}).get('period', 20)
        self.bb_std_dev: float = indicators_config.get('bollinger', {}).get('stdDev', 2)
        
        # ADX parameters
        self.adx_period: int = indicators_config.get('adx', {}).get('period', 14)
        self.adx_threshold: float = indicators_config.get('adx', {}).get('threshold', 20)
        
        # New risk management parameters
        self.min_adx_trend: float = indicators_config.get('min_adx_trend', 18)  # More realistic trend requirement
        self.bb_squeeze_threshold: float = indicators_config.get('bb_squeeze_threshold', 0.008)  # More realistic BB width threshold
        
        # Trading parameters
        trading_config = config.get('trading', {})
        self.position_size: float = trading_config.get('positionSize', 0.1)
        self.leverage: int = trading_config.get('leverage', 5)
        self.stop_loss_pct: float = trading_config.get('stop_loss_pct', 0.015)
        self.take_profit_pct: float = trading_config.get('take_profit_pct', 0.03)
        self.max_consecutive_losses: int = trading_config.get('max_consecutive_losses', 3)
        
        # Performance tracking
        self.consecutive_losses = 0
        self.total_trades = 0
        self.winning_trades = 0
        
        # Track evaluated data points to prevent duplicate exit signals
        self.evaluated_exit_points = set()
        
        self.logger.info(f"BBRSI Strategy initialized with RSI({self.rsi_period}), BB({self.bb_period}, {self.bb_std_dev}), ADX({self.adx_period})")
    
    def compute_indicators(self, data: List[Dict[str, Any]], index: int) -> Dict[str, Any]:
        """
        Compute technical indicators for the given data point.
        
        Args:
            data: Historical market data
            index: Current data index
            
        Returns:
            Dictionary containing computed indicators
        """
        # Debug logging to see what data we're receiving
        self.logger.debug(f"Index {index}: Data type: {type(data)}, Data length: {len(data) if hasattr(data, '__len__') else 'N/A'}")
        if data and len(data) > 0:
            self.logger.debug(f"Index {index}: First data item: {data[0] if isinstance(data, (list, tuple)) else 'Not list/tuple'}")
            if index < len(data):
                self.logger.debug(f"Index {index}: Current data item: {data[index]}")
        
        # Debug the max calculation
        max_period = max(self.rsi_period, self.bb_period, self.adx_period)
        self.logger.debug(f"max_period: {max_period}, type: {type(max_period)}")
        start_idx = index - max_period
        end_idx = index + 1
        self.logger.debug(f"start_idx: {start_idx}, end_idx: {end_idx}")
        
        # Extract all price data using the same slice range (handle both string and numeric values)
        # Use 'close' for backtest data, 'c' for raw data
        closes = [float(candle.get('close', candle.get('c', 0))) for candle in data[start_idx:end_idx]]
        highs = [float(candle.get('high', candle.get('h', 0))) for candle in data[start_idx:end_idx]]
        lows = [float(candle.get('low', candle.get('l', 0))) for candle in data[start_idx:end_idx]]
        
        self.logger.debug(f"Extracted {len(closes)} price points for indicators")
        self.logger.debug(f"closes length: {len(closes)}, highs length: {len(highs)}, lows length: {len(lows)}")
        
        if index < max(self.rsi_period, self.bb_period, self.adx_period):
            self.logger.debug(f"Index {index}: Insufficient data for indicators (need {max(self.rsi_period, self.bb_period, self.adx_period)})")
            return {}
        
        # Calculate RSI
        rsi = calculate_rsi(closes, self.rsi_period)
        
        # Calculate Bollinger Bands
        bb = calculate_bollinger_bands(closes, self.bb_period, self.bb_std_dev)
        
        # Calculate ADX
        adx_data = calculate_adx(highs, lows, closes, self.adx_period)
        
        # Calculate volatility (BB width as percentage of price)
        current_price = float(data[index].get('close', data[index].get('c', 0)))
        bb_width = (bb['upper'] - bb['lower']) / current_price
        volatility = bb_width
        
        # Calculate microprice for enhanced market microstructure analysis
        current_data = data[start_idx:end_idx]
        microprice_data = calculate_microprice_from_ohlcv(current_data, -1)
        
        # Debug logging
        self.logger.debug(f"Index {index}: Indicators computed - RSI: {rsi:.2f}, BB: {bb}, ADX: {adx_data['adx']:.2f}, Volatility: {volatility:.4f}")
        if microprice_data:
            self.logger.debug(f"Index {index}: Microprice: {microprice_data.microprice:.4f}, Volume Imbalance: {microprice_data.volume_imbalance:.3f}")
        
        return {
            'rsi': rsi,
            'bollinger': bb,
            'adx': adx_data['adx'],
            'plus_di': adx_data['plus_di'],
            'minus_di': adx_data['minus_di'],
            'volatility': volatility,
            'microprice_data': microprice_data
        }
    
    def generate_signal(self, data: List[Dict[str, Any]], index: int) -> Signal:
        """
        Generate a trading signal based on current market conditions.
        
        Args:
            data: Historical market data
            index: Current data index
            
        Returns:
            Signal object indicating trading action
        """
        # Compute indicators
        indicators = self.compute_indicators(data, index)
        if not indicators:
            return Signal('NONE', 0.0, 'Insufficient data for indicators', {}, 0.0, '', 0.0)
        
        # Extract indicator values
        rsi = indicators['rsi']
        bb = indicators['bollinger']
        adx = indicators['adx']
        plus_di = indicators['plus_di']
        minus_di = indicators['minus_di']
        volatility = indicators['volatility']
        
        current_price = float(data[index].get('close', data[index].get('c', 0)))
        
        # For backtesting, we don't check current position state
        # as we want to generate signals based purely on market conditions
        
        # Debug logging
        self.logger.debug(f"Index {index}: RSI={rsi:.2f}, BB_lower={bb['lower']:.2f}, BB_upper={bb['upper']:.2f}, Volatility={volatility:.4f}")
        
        # For backtesting, we'll skip the consecutive losses check
        # as we want to see all potential signals
        
        # Check volatility (avoid low volatility periods)
        if volatility < self.bb_squeeze_threshold * 0.1:  # Much more aggressive
            return Signal('NONE', 0.0, f'Extremely low volatility: {volatility:.4f}', {}, 0.0, '', 0.0)
        
        # Calculate BB position (0 = at lower band, 1 = at upper band)
        bb_position = (current_price - bb['lower']) / (bb['upper'] - bb['lower']) if bb['upper'] != bb['lower'] else 0.5
        
        # Calculate RSI momentum
        rsi_momentum = 0
        if index > 0:
            prev_rsi = self.compute_indicators(data, index - 1)
            if prev_rsi and 'rsi' in prev_rsi:
                rsi_momentum = rsi - prev_rsi['rsi']
        
        # EXIT SIGNAL LOGIC (NEW) - Generate exit signals to close positions
        # Exit LONG positions when conditions become bearish (more aggressive)
        if bb_position > 0.6 and rsi > 55:  # More aggressive exit
            exit_reason = f"Exit LONG: Price above middle BB ({bb_position:.3f}) + RSI high ({rsi:.2f})"
            self.logger.debug(f"Creating exit signal: {exit_reason}")
            return Signal('CLOSE_LONG', 1.0, exit_reason, {
                'rsi': rsi,
                'bb_position': bb_position,
                'price': current_price,
                'volatility': volatility,
                'exit_reason': 'BB middle + RSI high'
            }, current_price, self.market, data[index].get('timestamp', 0), 0.0)
        
        # Exit SHORT positions when conditions become bullish (more aggressive)
        if bb_position < 0.4 and rsi < 45:  # More aggressive exit
            exit_reason = f"Exit SHORT: Price below middle BB ({bb_position:.3f}) + RSI low ({rsi:.2f})"
            self.logger.debug(f"Creating exit signal: {exit_reason}")
            return Signal('CLOSE_SHORT', 1.0, exit_reason, {
                'rsi': rsi,
                'bb_position': bb_position,
                'price': current_price,
                'volatility': volatility,
                'exit_reason': 'BB middle + RSI low'
            }, current_price, self.market, data[index].get('timestamp', 0), 0.0)
        
        # Take profit exits (when price moves significantly in our favor) - more aggressive
        # For LONG positions: exit when price moves above middle BB with moderate RSI
        if bb_position > 0.55 and rsi > 60:  # More aggressive take profit
            exit_reason = f"Take Profit LONG: Price above middle BB ({bb_position:.3f}) + RSI moderate ({rsi:.2f})"
            self.logger.debug(f"Creating take profit signal: {exit_reason}")
            return Signal('CLOSE_LONG', 1.0, exit_reason, {
                'rsi': rsi,
                'bb_position': bb_position,
                'price': current_price,
                'volatility': volatility,
                'exit_reason': 'Take profit - price above middle BB + moderate RSI'
            }, current_price, self.market, data[index].get('timestamp', 0), 0.0)
        
        # For SHORT positions: exit when price moves below middle BB with moderate RSI
        if bb_position < 0.45 and rsi < 40:  # More aggressive take profit
            exit_reason = f"Take Profit SHORT: Price below middle BB ({bb_position:.3f}) + RSI moderate ({rsi:.2f})"
            self.logger.debug(f"Creating take profit signal: {exit_reason}")
            return Signal('CLOSE_SHORT', 1.0, exit_reason, {
                'rsi': rsi,
                'bb_position': bb_position,
                'price': current_price,
                'volatility': volatility,
                'exit_reason': 'Take profit - price below middle BB + moderate RSI'
            }, current_price, self.market, data[index].get('timestamp', 0), 0.0)
        
        # Quick profit exits (very aggressive)
        # For LONG positions: exit on any significant upward move
        if bb_position > 0.65 and rsi > 50:
            exit_reason = f"Quick Profit LONG: Price in upper range ({bb_position:.3f}) + RSI above neutral ({rsi:.2f})"
            self.logger.debug(f"Creating quick profit signal: {exit_reason}")
            return Signal('CLOSE_LONG', 1.0, exit_reason, {
                'rsi': rsi,
                'bb_position': bb_position,
                'price': current_price,
                'volatility': volatility,
                'exit_reason': 'Quick profit - upper range + RSI above neutral'
            }, current_price, self.market, data[index].get('timestamp', 0), 0.0)
        
        # For SHORT positions: exit on any significant downward move
        if bb_position < 0.35 and rsi < 50:
            exit_reason = f"Quick Profit SHORT: Price in lower range ({bb_position:.3f}) + RSI below neutral ({rsi:.2f})"
            self.logger.debug(f"Creating quick profit signal: {exit_reason}")
            return Signal('CLOSE_SHORT', 1.0, exit_reason, {
                'rsi': rsi,
                'bb_position': bb_position,
                'price': current_price,
                'volatility': volatility,
                'exit_reason': 'Quick profit - lower range + RSI below neutral'
            }, current_price, self.market, data[index].get('timestamp', 0), 0.0)
        
        # IMPROVED LONG signal conditions with better logic
        long_signals = []
        long_score = 0
        
        # 1. RSI conditions (more aggressive)
        if rsi < 40:  # More aggressive oversold
            long_score += 3
            long_signals.append('RSI strongly oversold')
        elif rsi < 50:  # More aggressive moderate oversold
            long_score += 2
            long_signals.append('RSI oversold')
        elif rsi < 60:  # More aggressive below neutral
            long_score += 1
            long_signals.append('RSI below neutral')
        
        # 2. Bollinger Band conditions (more aggressive)
        if bb_position < 0.3:  # More aggressive near lower band
            long_score += 3
            long_signals.append('Price at lower BB')
        elif bb_position < 0.4:  # More aggressive below lower third
            long_score += 2
            long_signals.append('Price below lower third')
        elif bb_position < 0.6:  # More aggressive below middle
            long_score += 1
            long_signals.append('Price below middle BB')
        
        # 3. RSI momentum (trend confirmation)
        if rsi_momentum > 2:  # Strong upward momentum
            long_score += 2
            long_signals.append('RSI momentum strong')
        elif rsi_momentum > 0:  # Positive momentum
            long_score += 1
            long_signals.append('RSI momentum positive')
        
        # 4. Volatility confirmation
        if volatility > self.bb_squeeze_threshold * 2:  # High volatility
            long_score += 1
            long_signals.append('High volatility')
        
        # 5. Trend strength (ADX) - enhanced
        if adx > self.adx_threshold and plus_di > minus_di:
            long_score += 2
            long_signals.append('Strong uptrend')
        elif plus_di > minus_di:
            long_score += 1
            long_signals.append('Weak uptrend')
        
        # 6. Microprice analysis for enhanced market microstructure insights
        microprice_data = indicators.get('microprice_data')
        if microprice_data:
            microprice_signals = get_microprice_signals(microprice_data, threshold=0.0005)
            volume_imbalance = abs(microprice_data.volume_imbalance)
            
            # Microprice confirmation for LONG signals
            if microprice_signals['signal'] == 'BULLISH':
                long_score += 2
                long_signals.append('Microprice bullish confirmation')
            elif microprice_signals['signal'] == 'NONE' and volume_imbalance < 0.2:
                long_score += 1
                long_signals.append('Microprice neutral, balanced volume')
            elif microprice_signals['signal'] == 'BEARISH':
                long_score -= 1  # Reduce score if microprice contradicts
                long_signals.append('Microprice bearish (reducing score)')
            
            # Volume imbalance analysis
            if volume_imbalance > 0.3:
                long_score += 1
                long_signals.append('Strong volume imbalance')
        
        # 7. Market regime filter - only trade in favorable conditions
        if adx < 15:  # Low trend strength - avoid ranging markets
            long_score -= 2
            long_signals.append('Low trend strength - AVOID')
        
        # 7. Volatility regime - prefer moderate volatility
        if volatility > 0.01:  # Too high volatility
            long_score -= 1
            long_signals.append('High volatility - CAUTION')
        elif volatility < 0.001:  # Too low volatility
            long_score -= 1
            long_signals.append('Low volatility - AVOID')
        
        # IMPROVED SHORT signal conditions with better logic
        short_signals = []
        short_score = 0
        
        # 1. RSI conditions (balanced approach)
        if rsi > 65:  # Strong overbought
            short_score += 3
            short_signals.append('RSI strongly overbought')
        elif rsi > 60:  # Moderate overbought
            short_score += 2
            short_signals.append('RSI overbought')
        elif rsi > 50:  # Above neutral
            short_score += 1
            short_signals.append('RSI above neutral')
        
        # 2. Bollinger Band conditions (mean reversion focus)
        if bb_position > 0.8:  # Near upper band
            short_score += 3
            short_signals.append('Price at upper BB')
        elif bb_position > 0.7:  # Above upper third
            short_score += 2
            short_signals.append('Price above upper third')
        elif bb_position > 0.5:  # Above middle
            short_score += 1
            short_signals.append('Price above middle BB')
        
        # 3. RSI momentum (trend confirmation)
        if rsi_momentum < -2:  # Strong downward momentum
            short_score += 2
            short_signals.append('RSI momentum strong')
        elif rsi_momentum < 0:  # Negative momentum
            short_score += 1
            short_signals.append('RSI momentum negative')
        
        # 4. Volatility confirmation
        if volatility > self.bb_squeeze_threshold * 2:  # High volatility
            short_score += 1
            short_signals.append('High volatility')
        
        # 5. Trend strength (ADX)
        if adx > self.adx_threshold and minus_di > plus_di:
            short_score += 2
            short_signals.append('Strong downtrend')
        elif minus_di > plus_di:
            short_score += 1
            short_signals.append('Weak downtrend')
        
        # 6. Microprice analysis for SHORT signals
        if microprice_data:
            # Microprice confirmation for SHORT signals
            if microprice_signals['signal'] == 'BEARISH':
                short_score += 2
                short_signals.append('Microprice bearish confirmation')
            elif microprice_signals['signal'] == 'NONE' and volume_imbalance < 0.2:
                short_score += 1
                short_signals.append('Microprice neutral, balanced volume')
            elif microprice_signals['signal'] == 'BULLISH':
                short_score -= 1  # Reduce score if microprice contradicts
                short_signals.append('Microprice bullish (reducing score)')
            
            # Volume imbalance analysis for SHORT
            if volume_imbalance > 0.3:
                short_score += 1
                short_signals.append('Strong volume imbalance')
        
        # Debug logging for signal conditions
        self.logger.debug(f"Signal conditions - Long score: {long_score}, Short score: {short_score}")
        self.logger.debug(f"Long signals: {long_signals}")
        self.logger.debug(f"Short signals: {short_signals}")
        self.logger.debug(f"RSI: {rsi:.2f} (momentum: {rsi_momentum:.2f})")
        self.logger.debug(f"Price: {current_price:.2f} (BB position: {bb_position:.3f})")
        self.logger.debug(f"Volatility: {volatility:.4f} (threshold: {self.bb_squeeze_threshold})")
        
        # Generate signals - require minimum score for entry (trend-following approach)
        min_score = 3  # Lower threshold for more opportunities while maintaining quality
        
        if long_score >= min_score:
            signal_strength = min(1.0, long_score / 8.0)  # Normalize to 0-1
            signal_reason = f"LONG: {', '.join(long_signals)} (Score: {long_score})"
            
            self.logger.debug(f"Creating LONG signal: {signal_reason} with strength {signal_strength}")
            # Calculate stop loss (1.5% below entry for more aggressive trading)
            stop_loss = current_price * 0.985
            signal = Signal('LONG', signal_strength, signal_reason, {
                'rsi': rsi,
                'rsi_momentum': rsi_momentum,
                'bb_position': bb_position,
                'price': current_price,
                'volatility': volatility,
                'score': long_score,
                'signals': long_signals,
                'microprice': microprice_data.microprice if microprice_data else None,
                'microprice_signal': microprice_signals['signal'] if microprice_data else None,
                'volume_imbalance': microprice_data.volume_imbalance if microprice_data else None
            }, current_price, self.market, data[index].get('timestamp', 0), stop_loss)
            self.logger.debug(f"Generated LONG signal: {signal}")
            return signal
        
        elif short_score >= min_score:
            signal_strength = min(1.0, short_score / 8.0)  # Normalize to 0-1
            signal_reason = f"SHORT: {', '.join(short_signals)} (Score: {short_score})"
            
            self.logger.debug(f"Creating SHORT signal: {signal_reason} with strength {signal_strength}")
            # Calculate stop loss (1.5% above entry for more aggressive trading)
            stop_loss = current_price * 1.015
            signal = Signal('SHORT', signal_strength, signal_reason, {
                'rsi': rsi,
                'rsi_momentum': rsi_momentum,
                'bb_position': bb_position,
                'price': current_price,
                'volatility': volatility,
                'score': short_score,
                'signals': short_signals,
                'microprice': microprice_data.microprice if microprice_data else None,
                'microprice_signal': microprice_signals['signal'] if microprice_data else None,
                'volume_imbalance': microprice_data.volume_imbalance if microprice_data else None
            }, current_price, self.market, data[index].get('timestamp', 0), stop_loss)
            self.logger.debug(f"Generated SHORT signal: {signal}")
            return signal
        
        signal = Signal('NONE', 0.0, f'No entry criteria met (Long: {long_score}, Short: {short_score})', {}, 0.0, '', 0.0)
        self.logger.debug(f"Generated NONE signal: {signal}")
        return signal
    
    def reset_for_backtest(self):
        """
        Reset strategy state for a new backtest.
        This ensures clean state and prevents issues from previous runs.
        """
        self.evaluated_exit_points.clear()
        self.logger.debug("Strategy reset for new backtest")
    
    def evaluate_position(self, data: List[Dict[str, Any]], index: int) -> Signal:
        """
        Evaluate current positions and determine if any should be closed.
        
        Args:
            data: Historical market data
            index: Current data index
            
        Returns:
            Signal object for position management
        """
        # Check if we've already evaluated this data point for exit signals
        # This prevents duplicate exit signal generation
        if index in self.evaluated_exit_points:
            return Signal('NONE', 0.0, 'Already evaluated for exit', {}, 0.0, '', 0.0)
        
        # Mark this data point as evaluated
        self.evaluated_exit_points.add(index)
        
        current_price = float(data[index].get('close', data[index].get('c', 0)))
        
        # Check if we should exit based on market conditions
        indicators = self.compute_indicators(data, index)
        if not indicators:
            return Signal('NONE', 0.0, 'No indicators available', {}, 0.0, '', 0.0)
        
        # Check for exit conditions based on market conditions
        if 'bollinger' in indicators:
            bb = indicators['bollinger']
            bb_middle = bb['middle']
            
            # Exit if price returns to middle BB (mean reversion) - optimized for profit
            if abs(current_price - bb_middle) / bb_middle < 0.001:  # Within 0.1% of middle (maximize profit)
                reason = f'Mean reversion exit: price near middle BB ({bb_middle:.2f})'
                # Return a generic exit signal - the trading engine will determine which positions to close
                return Signal('CLOSE_ALL', 0.8, reason, {'bb_middle': bb_middle}, current_price, self.market, data[index].get('timestamp', 0))
        
        # Check for profit target exit
        if self.current_position:
            entry_price = self.current_position.entry_price
            if self.current_position.side == 'LONG':
                profit_pct = (current_price - entry_price) / entry_price
            else:  # SHORT
                profit_pct = (entry_price - current_price) / entry_price
            
            # Take profit at 0.15% (very aggressive for better profitability)
            if profit_pct >= 0.0015:
                reason = f'Profit target exit: {profit_pct:.2%}'
                return Signal('CLOSE_ALL', 0.9, reason, {'profit_pct': profit_pct}, current_price, self.market, data[index].get('timestamp', 0))
        
        # Check for time-based exit (prevent holding too long)
        if self.current_position:
            from datetime import datetime
            entry_time = datetime.fromisoformat(self.current_position.entry_time.replace('Z', '+00:00'))
            current_time = datetime.now()
            hold_time = (current_time - entry_time).total_seconds()
            
            # Exit after 3 minutes to prevent long holds
            if hold_time >= 180:  # 3 minutes
                reason = f'Time-based exit: {hold_time:.0f}s'
                return Signal('CLOSE_ALL', 0.8, reason, {'hold_time': hold_time}, current_price, self.market, data[index].get('timestamp', 0))
        
        # Check for extreme market conditions that warrant closing all positions
        if 'rsi' in indicators:
            rsi = indicators['rsi']
            if rsi > 80 or rsi < 20:  # Extreme RSI values
                reason = f'Extreme RSI exit: {rsi:.2f}'
                return Signal('CLOSE_ALL', 0.9, reason, {'rsi': rsi}, current_price, self.market, data[index].get('timestamp', 0))
        
        return Signal('NONE', 0.0, 'Positions held', {}, 0.0, '', 0.0)
    
    def update_position(self, position: Optional[Position]):
        """
        Update the current position and track performance.
        
        Args:
            position: New position or None to clear position
        """
        if self.current_position and position is None:
            # Position was closed, update statistics
            self.total_trades += 1
            # Note: In a real implementation, you'd calculate actual P&L here
        
        super().update_position(position)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get strategy-specific performance statistics.
        
        Returns:
            Dictionary containing performance metrics
        """
        base_stats = super().get_performance_stats()
        
        # Add BBRSI-specific metrics
        bb_stats = {
            'consecutive_losses': self.consecutive_losses,
            'max_consecutive_losses': self.max_consecutive_losses,
            'rsi_period': self.rsi_period,
            'bb_period': self.bb_period,
            'adx_period': self.adx_period,
            'volatility_threshold': self.bb_squeeze_threshold,
            'trend_threshold': self.min_adx_trend
        }
        
        return {**base_stats, **bb_stats}
    
    def validate_config(self) -> bool:
        """
        Validate BBRSI strategy configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        # Call parent validation
        if not super().validate_config():
            return False
        
        # Validate indicator parameters
        if self.rsi_period <= 0:
            self.logger.error("RSI period must be positive")
            return False
        
        if self.rsi_overbought <= 50 or self.rsi_oversold >= 50:
            self.logger.error("RSI overbought must be > 50 and oversold must be < 50")
            return False
        
        if self.bb_period <= 0:
            self.logger.error("Bollinger Bands period must be positive")
            return False
        
        if self.adx_period <= 0:
            self.logger.error("ADX period must be positive")
            return False
        
        if self.bb_squeeze_threshold <= 0:
            self.logger.error("BB squeeze threshold must be positive")
            return False
        
        return True
