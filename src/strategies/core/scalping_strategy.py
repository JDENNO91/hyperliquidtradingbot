"""
Scalping Strategy

A high-frequency trading strategy designed for short-term opportunities with quick entry/exit.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.core.base_strategy import BaseStrategy, Signal, Position
# Microprice functionality removed - using simpler indicators

class ScalpingStrategy(BaseStrategy):
    """
    Scalping Strategy Implementation
    
    This strategy focuses on:
    1. Quick entry/exit based on price action
    2. Tight risk management
    3. High-frequency trading opportunities
    4. Volume-based confirmation
    
    Entry Conditions:
    - LONG: Price momentum + volume spike + short-term oversold
    - SHORT: Price momentum + volume spike + short-term overbought
    
    Exit Conditions:
    - Quick profit target (0.5-1.0%)
    - Tight stop loss (0.3-0.5%)
    - Time-based exit (max hold time)
    """
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        Initialize scalping strategy with configuration.
        
        Args:
            config: Strategy configuration dictionary
            logger: Logger instance
        """
        super().__init__(config, logger)
        
        # Extract trading configuration
        trading_config = config.get('trading', {})
        
        # Scalping-specific parameters
        self.entry_threshold = trading_config.get('entry_threshold', 0.002)  # 0.2% price movement
        self.exit_threshold = trading_config.get('exit_threshold', 0.005)    # 0.5% profit target
        self.max_hold_time = trading_config.get('max_hold_time', 300)       # 5 minutes max
        self.volume_multiplier = trading_config.get('volume_multiplier', 1.5)  # Volume spike threshold
        
        # Risk management
        self.stop_loss_pct = trading_config.get('stop_loss_pct', 0.003)     # 0.3% stop loss
        self.max_position_size = trading_config.get('max_position_size', 0.05)  # 5% max position
        
        # Performance tracking
        self.total_scalps = 0
        self.successful_scalps = 0
        self.avg_hold_time = 0.0
        
        self.logger.info(f"Scalping Strategy initialized with entry threshold: {self.entry_threshold:.1%}")
    
    def compute_indicators(self, data: List[Dict[str, Any]], index: int) -> Dict[str, Any]:
        """
        Compute indicators for scalping strategy with improved logic.
        
        Args:
            data: Historical market data
            index: Current data index
            
        Returns:
            Dictionary containing computed indicators
        """
        if index < 20:  # Need at least 20 candles for basic calculations
            return {}
        
        # Extract recent price data (handle both formats)
        recent_closes = [float(candle.get('close', candle.get('c', 0))) for candle in data[index-20:index+1]]
        recent_volumes = [float(candle.get('volume', candle.get('v', 0))) for candle in data[index-20:index+1]]
        recent_highs = [float(candle.get('high', candle.get('h', 0))) for candle in data[index-20:index+1]]
        recent_lows = [float(candle.get('low', candle.get('l', 0))) for candle in data[index-20:index+1]]
        
        # Calculate price momentum (multiple timeframes)
        current_price = recent_closes[-1]
        prev_price = recent_closes[-2]
        price_change_1m = (current_price - prev_price) / prev_price
        
        # 5-minute momentum
        price_change_5m = (current_price - recent_closes[-6]) / recent_closes[-6] if len(recent_closes) >= 6 else 0
        
        # Calculate volume spike (improved)
        current_volume = recent_volumes[-1]
        avg_volume = sum(recent_volumes[:-1]) / len(recent_volumes[:-1])
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        
        # Calculate short-term volatility (ATR-like)
        true_ranges = []
        for i in range(1, len(recent_closes)):
            tr = max(
                recent_highs[i] - recent_lows[i],
                abs(recent_highs[i] - recent_closes[i-1]),
                abs(recent_lows[i] - recent_closes[i-1])
            )
            true_ranges.append(tr)
        atr = sum(true_ranges) / len(true_ranges) if true_ranges else 0
        volatility = atr / current_price if current_price > 0 else 0
        
        # Calculate price acceleration (second derivative)
        price_acceleration = 0
        if len(recent_closes) >= 3:
            accel1 = (recent_closes[-1] - recent_closes[-2]) / recent_closes[-2]
            accel2 = (recent_closes[-2] - recent_closes[-3]) / recent_closes[-3]
            price_acceleration = accel1 - accel2
        
        # Calculate support/resistance levels
        recent_high = max(recent_highs[-10:])  # 10-period high
        recent_low = min(recent_lows[-10:])    # 10-period low
        price_position = (current_price - recent_low) / (recent_high - recent_low) if recent_high != recent_low else 0.5
        
        # Calculate microprice for enhanced scalping signals
        current_data = data[index-20:index+1]
        microprice_data = calculate_microprice_from_ohlcv(current_data, -1)
        
        return {
            'price_change_1m': price_change_1m,
            'price_change_5m': price_change_5m,
            'price_acceleration': price_acceleration,
            'volume_ratio': volume_ratio,
            'volatility': volatility,
            'price_position': price_position,
            'current_price': current_price,
            'current_volume': current_volume,
            'atr': atr,
            'microprice_data': microprice_data
        }
    
    def generate_signal(self, data: List[Dict[str, Any]], index: int) -> Signal:
        """
        Generate scalping signal based on price action and volume.
        
        Args:
            data: Historical market data
            index: Current data index
            
        Returns:
            Signal object indicating trading action
        """
        # Compute indicators
        indicators = self.compute_indicators(data, index)
        if not indicators:
            return Signal('NONE', 0.0, 'Insufficient data for indicators', {})
        
        # Check if we have a position
        if self.current_position:
            return Signal('NONE', 0.0, 'Position already open', {})
        
        # Extract indicator values
        price_change_1m = indicators['price_change_1m']
        price_change_5m = indicators['price_change_5m']
        price_acceleration = indicators['price_acceleration']
        volume_ratio = indicators['volume_ratio']
        volatility = indicators['volatility']
        price_position = indicators['price_position']
        current_price = indicators['current_price']
        
        # IMPROVED LONG signal conditions
        long_score = 0
        long_signals = []
        
        # 1. Price momentum (1m and 5m alignment) - extremely aggressive for more trades
        if price_change_1m > self.entry_threshold * 0.2:  # Very low threshold (0.1%)
            long_score += 2
            long_signals.append('1m momentum up')
        if price_change_5m > -0.005:  # Extremely lenient 5m momentum
            long_score += 1
            long_signals.append('5m momentum up')
        
        # 2. Price acceleration - more lenient
        if price_acceleration > 0.0005:  # More lenient acceleration
            long_score += 2
            long_signals.append('Price acceleration')
        
        # 3. Volume confirmation - very lenient for more trades
        if volume_ratio > self.volume_multiplier:
            long_score += 2
            long_signals.append('Volume spike')
        elif volume_ratio > 1.05:  # Very lenient volume requirement (5% above average)
            long_score += 1
            long_signals.append('Volume above average')
        
        # 4. Volatility check - very lenient for more trades
        if volatility > 0.0005:  # Very lenient volatility requirement
            long_score += 1
            long_signals.append('High volatility')
        
        # 5. Price position (support/resistance)
        if price_position < 0.3:  # Near support
            long_score += 1
            long_signals.append('Near support')
        
        # 6. Multi-timeframe confirmation
        if price_change_1m > 0 and price_change_5m > 0:  # Both timeframes aligned
            long_score += 2
            long_signals.append('Multi-timeframe alignment')
        
        # 7. Volume-price relationship
        if price_change_1m > 0 and volume_ratio > 1.3:  # Price up with volume
            long_score += 1
            long_signals.append('Volume-price confirmation')
        
        # 8. Market regime filter - less restrictive for more trades
        if volatility < 0.0002:  # Only avoid extremely low volatility
            long_score -= 2
            long_signals.append('Very low volatility - CAUTION')
        elif volatility > 0.01:  # Only avoid extremely high volatility
            long_score -= 1
            long_signals.append('Very high volatility - CAUTION')
        
        # 9. Microprice analysis for enhanced scalping precision
        microprice_data = indicators.get('microprice_data')
        if microprice_data:
            microprice_signals = get_microprice_signals(microprice_data, threshold=0.0003)  # Lower threshold for scalping
            volume_imbalance = abs(microprice_data.volume_imbalance)
            
            # Microprice confirmation for LONG scalping
            if microprice_signals['signal'] == 'BULLISH':
                long_score += 2
                long_signals.append('Microprice bullish confirmation')
            elif microprice_signals['signal'] == 'NONE' and volume_imbalance < 0.15:
                long_score += 1
                long_signals.append('Microprice neutral, balanced')
            elif microprice_signals['signal'] == 'BEARISH':
                long_score -= 1
                long_signals.append('Microprice bearish (reducing)')
            
            # Volume imbalance for scalping
            if volume_imbalance > 0.25:
                long_score += 1
                long_signals.append('Strong volume imbalance')
        
        # IMPROVED SHORT signal conditions
        short_score = 0
        short_signals = []
        
        # 1. Price momentum (1m and 5m alignment)
        if price_change_1m < -self.entry_threshold:
            short_score += 2
            short_signals.append('1m momentum down')
        if price_change_5m < 0:
            short_score += 1
            short_signals.append('5m momentum down')
        
        # 2. Price acceleration
        if price_acceleration < -0.001:  # Accelerating downward
            short_score += 2
            short_signals.append('Price acceleration')
        
        # 3. Volume confirmation
        if volume_ratio > self.volume_multiplier:
            short_score += 2
            short_signals.append('Volume spike')
        elif volume_ratio > 1.2:
            short_score += 1
            short_signals.append('Volume above average')
        
        # 4. Volatility check
        if volatility > 0.002:  # Sufficient volatility
            short_score += 1
            short_signals.append('High volatility')
        
        # 5. Price position (support/resistance)
        if price_position > 0.7:  # Near resistance
            short_score += 1
            short_signals.append('Near resistance')
        
        # 6. Microprice analysis for SHORT scalping
        if microprice_data:
            # Microprice confirmation for SHORT scalping
            if microprice_signals['signal'] == 'BEARISH':
                short_score += 2
                short_signals.append('Microprice bearish confirmation')
            elif microprice_signals['signal'] == 'NONE' and volume_imbalance < 0.15:
                short_score += 1
                short_signals.append('Microprice neutral, balanced')
            elif microprice_signals['signal'] == 'BULLISH':
                short_score -= 1
                short_signals.append('Microprice bullish (reducing)')
            
            # Volume imbalance for SHORT scalping
            if volume_imbalance > 0.25:
                short_score += 1
                short_signals.append('Strong volume imbalance')
        
        # Generate signals with minimum score requirement - extremely aggressive for more trades
        min_score = 1  # Extremely low threshold for maximum opportunities
        
        if long_score >= min_score:
            signal_strength = min(1.0, long_score / 8.0)
            return Signal('LONG', signal_strength, f'Scalp LONG: {", ".join(long_signals)} (Score: {long_score})', {
                'price_change_1m': price_change_1m,
                'price_change_5m': price_change_5m,
                'price_acceleration': price_acceleration,
                'volume_ratio': volume_ratio,
                'volatility': volatility,
                'price_position': price_position,
                'score': long_score,
                'microprice': microprice_data.microprice if microprice_data else None,
                'microprice_signal': microprice_signals['signal'] if microprice_data else None,
                'volume_imbalance': microprice_data.volume_imbalance if microprice_data else None
            }, current_price, self.market, data[index].get('timestamp', 0), current_price * 0.997)
        
        elif short_score >= min_score:
            signal_strength = min(1.0, short_score / 8.0)
            return Signal('SHORT', signal_strength, f'Scalp SHORT: {", ".join(short_signals)} (Score: {short_score})', {
                'price_change_1m': price_change_1m,
                'price_change_5m': price_change_5m,
                'price_acceleration': price_acceleration,
                'volume_ratio': volume_ratio,
                'volatility': volatility,
                'price_position': price_position,
                'score': short_score,
                'microprice': microprice_data.microprice if microprice_data else None,
                'microprice_signal': microprice_signals['signal'] if microprice_data else None,
                'volume_imbalance': microprice_data.volume_imbalance if microprice_data else None
            }, current_price, self.market, data[index].get('timestamp', 0), current_price * 1.003)
        
        return Signal('NONE', 0.0, 'No scalping opportunity', {})
    
    def evaluate_position(self, data: List[Dict[str, Any]], index: int) -> Signal:
        """
        Evaluate current position for scalping exit conditions.
        
        Args:
            data: Historical market data
            index: Current data index
            
        Returns:
            Signal object for position management
        """
        if not self.current_position:
            return Signal('NONE', 0.0, 'No position to evaluate', {})
        
        current_price = data[index]['close']
        entry_price = self.current_position.entry_price
        entry_time = datetime.fromisoformat(self.current_position.entry_time.replace('Z', '+00:00'))
        current_time = datetime.now()
        
        # Calculate P&L
        if self.current_position.side == 'LONG':
            pnl_pct = (current_price - entry_price) / entry_price
        else:  # SHORT
            pnl_pct = (entry_price - current_price) / entry_price
        
        # Check take profit - optimized for better returns
        if pnl_pct >= self.exit_threshold * 0.8:  # Take profit at 80% of target (0.4% instead of 0.5%)
            reason = f'Scalp take profit: {pnl_pct:.2%}'
            if self.current_position.side == 'LONG':
                return Signal('CLOSE_LONG', 1.0, reason, {'pnl_pct': pnl_pct})
            else:
                return Signal('CLOSE_SHORT', 1.0, reason, {'pnl_pct': pnl_pct})
        
        # Check stop loss
        if pnl_pct <= -self.stop_loss_pct:
            reason = f'Scalp stop loss: {pnl_pct:.2%}'
            if self.current_position.side == 'LONG':
                return Signal('CLOSE_LONG', 1.0, reason, {'pnl_pct': pnl_pct})
            else:
                return Signal('CLOSE_SHORT', 1.0, reason, {'pnl_pct': pnl_pct})
        
        # Check time-based exit
        hold_time = (current_time - entry_time).total_seconds()
        if hold_time > self.max_hold_time:
            reason = f'Time-based exit: held for {hold_time:.0f}s (max: {self.max_hold_time}s)'
            if self.current_position.side == 'LONG':
                return Signal('CLOSE_LONG', 0.8, reason, {'hold_time': hold_time})
            else:
                return Signal('CLOSE_SHORT', 0.8, reason, {'hold_time': hold_time})
        
        return Signal('NONE', 0.0, 'Position held', {})
    
    def update_position(self, position: Optional[Position]):
        """
        Update the current position and track scalping performance.
        
        Args:
            position: New position or None to clear position
        """
        if self.current_position and position is None:
            # Position was closed, update scalping statistics
            self.total_scalps += 1
            # Note: In a real implementation, you'd calculate actual P&L here
        
        super().update_position(position)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get scalping-specific performance statistics.
        
        Returns:
            Dictionary containing performance metrics
        """
        base_stats = super().get_performance_stats()
        
        # Add scalping-specific metrics
        scalp_stats = {
            'total_scalps': self.total_scalps,
            'successful_scalps': self.successful_scalps,
            'scalp_success_rate': self.successful_scalps / self.total_scalps if self.total_scalps > 0 else 0.0,
            'avg_hold_time': self.avg_hold_time,
            'entry_threshold': self.entry_threshold,
            'exit_threshold': self.exit_threshold,
            'max_hold_time': self.max_hold_time,
            'volume_multiplier': self.volume_multiplier
        }
        
        return {**base_stats, **scalp_stats}
    
    def validate_config(self) -> bool:
        """
        Validate scalping strategy configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        # Call parent validation
        if not super().validate_config():
            return False
        
        # Validate scalping parameters
        if self.entry_threshold <= 0:
            self.logger.error("Entry threshold must be positive")
            return False
        
        if self.exit_threshold <= 0:
            self.logger.error("Exit threshold must be positive")
            return False
        
        if self.max_hold_time <= 0:
            self.logger.error("Max hold time must be positive")
            return False
        
        if self.volume_multiplier <= 0:
            self.logger.error("Volume multiplier must be positive")
            return False
        
        if self.stop_loss_pct <= 0:
            self.logger.error("Stop loss percentage must be positive")
            return False
        
        return True