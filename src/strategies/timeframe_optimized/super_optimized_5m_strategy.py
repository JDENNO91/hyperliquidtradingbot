"""
Super Optimized 5m Strategy

Optimized for 5-minute timeframes with longer hold times and adjusted parameters.
"""

import logging
import math
import random
from typing import Dict, Any, Optional, List
from datetime import datetime

from core.base_strategy import BaseStrategy, Signal, Position

class SuperOptimized5mStrategy(BaseStrategy):
    """
    Super Optimized 5m Strategy Implementation
    
    This strategy is optimized for 5-minute timeframes:
    1. Longer hold times (60 seconds)
    2. Higher profit targets (2.5%)
    3. Adjusted momentum thresholds
    4. 5m-specific indicators
    """
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        Initialize super optimized 5m strategy with configuration.
        
        Args:
            config: Strategy configuration dictionary
            logger: Logger instance
        """
        super().__init__(config, logger)
        
        # Extract trading configuration
        trading_config = config.get('trading', {})
        
        # 5m optimized parameters
        self.momentum_threshold = 0.0005  # Higher threshold for 5m
        self.volume_threshold = 1.1  # Higher volume requirement for 5m
        self.volatility_threshold = 0.0005  # Higher volatility requirement for 5m
        
        # Exit parameters - optimized for 5m timeframes
        self.profit_target = 0.025  # 2.5% profit target for 5m
        self.stop_loss = 0.008  # 0.8% stop loss for 5m
        self.max_hold_time = 60  # 60 seconds max for 5m
        
        # AI ensemble weights - optimized for 5m
        self.ensemble_weights = {
            'momentum': 0.35,
            'neural_network': 0.25,
            'ml_features': 0.25,
            'volume_analysis': 0.15
        }
        
        # Performance tracking
        self.total_signals = 0
        self.executed_signals = 0
        self.successful_trades = 0
        self.recent_performance = []
        
        self.logger.info(f"Super Optimized 5m Strategy initialized for 5-minute timeframes")
    
    def compute_indicators(self, data: List[Dict[str, Any]], index: int) -> Dict[str, Any]:
        """
        Compute comprehensive indicators for 5m strategy.
        
        Args:
            data: Historical market data
            index: Current data index
            
        Returns:
            Dictionary containing computed indicators
        """
        if index < 30:  # Need more data for 5m
            return {}
        
        # Extract price data
        recent_closes = [float(candle.get('close', candle.get('c', 0))) for candle in data[index-30:index+1]]
        recent_highs = [float(candle.get('high', candle.get('h', 0))) for candle in data[index-30:index+1]]
        recent_lows = [float(candle.get('low', candle.get('l', 0))) for candle in data[index-30:index+1]]
        recent_volumes = [float(candle.get('volume', candle.get('v', 0))) for candle in data[index-30:index+1]]
        
        current_price = recent_closes[-1]
        
        # Multi-timeframe momentum for 5m
        momentum_1m = (current_price - recent_closes[-2]) / recent_closes[-2] if len(recent_closes) >= 2 else 0
        momentum_3m = (current_price - recent_closes[-4]) / recent_closes[-4] if len(recent_closes) >= 4 else 0
        momentum_5m = (current_price - recent_closes[-6]) / recent_closes[-6] if len(recent_closes) >= 6 else 0
        momentum_10m = (current_price - recent_closes[-11]) / recent_closes[-11] if len(recent_closes) >= 11 else 0
        momentum_15m = (current_price - recent_closes[-16]) / recent_closes[-16] if len(recent_closes) >= 16 else 0
        
        # Volume analysis
        current_volume = recent_volumes[-1]
        avg_volume = sum(recent_volumes[:-1]) / len(recent_volumes[:-1])
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        
        # Volatility features
        price_range = max(recent_highs[-15:]) - min(recent_lows[-15:])
        volatility = price_range / current_price if current_price > 0 else 0
        
        # Trend strength
        trend_strength = self._calculate_trend_strength(recent_closes)
        
        # Price acceleration
        acceleration = momentum_1m - momentum_5m if len(recent_closes) >= 6 else 0
        
        # Price position
        high_30 = max(recent_highs)
        low_30 = min(recent_lows)
        price_position = (current_price - low_30) / (high_30 - low_30) if high_30 > low_30 else 0.5
        
        # RSI momentum
        rsi_momentum = self._calculate_rsi_momentum(recent_closes)
        
        # Volume momentum
        volume_momentum = (current_volume - recent_volumes[-5]) / recent_volumes[-5] if len(recent_volumes) >= 6 else 0
        
        # Market regime
        market_regime = self._detect_market_regime(volatility, volume_ratio, trend_strength)
        
        return {
            'momentum_1m': momentum_1m,
            'momentum_3m': momentum_3m,
            'momentum_5m': momentum_5m,
            'momentum_10m': momentum_10m,
            'momentum_15m': momentum_15m,
            'volume_ratio': volume_ratio,
            'volatility': volatility,
            'trend_strength': trend_strength,
            'acceleration': acceleration,
            'price_position': price_position,
            'rsi_momentum': rsi_momentum,
            'volume_momentum': volume_momentum,
            'market_regime': market_regime,
            'current_price': current_price
        }
    
    def generate_signal(self, data: List[Dict[str, Any]], index: int) -> Signal:
        """
        Generate 5m optimized trading signal.
        
        Args:
            data: Historical market data
            index: Current data index
            
        Returns:
            Signal object indicating trading action
        """
        # Compute indicators
        indicators = self.compute_indicators(data, index)
        if not indicators:
            return Signal('NONE', 0.0, 'Insufficient data for 5m strategy', {})
        
        # Check if we have a position
        if self.current_position:
            return Signal('NONE', 0.0, 'Position already open', {})
        
        # Get predictions from all AI approaches
        predictions = {}
        
        # 1. Momentum prediction
        predictions['momentum'] = self._momentum_prediction(indicators)
        
        # 2. Neural network prediction
        predictions['neural_network'] = self._neural_network_prediction(indicators)
        
        # 3. ML features prediction
        predictions['ml_features'] = self._ml_features_prediction(indicators)
        
        # 4. Volume analysis prediction
        predictions['volume_analysis'] = self._volume_analysis_prediction(indicators)
        
        # Ensemble voting with weights
        ensemble_long_score = 0
        ensemble_short_score = 0
        
        for approach, prediction in predictions.items():
            weight = self.ensemble_weights[approach]
            if prediction > 0:  # Long signal
                ensemble_long_score += prediction * weight
            else:  # Short signal
                ensemble_short_score += abs(prediction) * weight
        
        # 5m optimized decision threshold
        threshold = 0.3  # Higher threshold for 5m
        
        # Generate signals
        if ensemble_long_score >= threshold and ensemble_long_score > ensemble_short_score:
            signal_strength = min(1.0, ensemble_long_score)
            return Signal('LONG', signal_strength, f'5m LONG: Score={ensemble_long_score:.3f}', {
                'ensemble_long_score': ensemble_long_score,
                'ensemble_short_score': ensemble_short_score,
                'predictions': predictions,
                'ensemble_weights': self.ensemble_weights,
                'indicators': indicators
            }, indicators['current_price'], self.market, data[index].get('timestamp', 0), indicators['current_price'] * 0.992)
        
        elif ensemble_short_score >= threshold and ensemble_short_score > ensemble_long_score:
            signal_strength = min(1.0, ensemble_short_score)
            return Signal('SHORT', signal_strength, f'5m SHORT: Score={ensemble_short_score:.3f}', {
                'ensemble_long_score': ensemble_long_score,
                'ensemble_short_score': ensemble_short_score,
                'predictions': predictions,
                'ensemble_weights': self.ensemble_weights,
                'indicators': indicators
            }, indicators['current_price'], self.market, data[index].get('timestamp', 0), indicators['current_price'] * 1.008)
        
        return Signal('NONE', 0.0, 'No 5m opportunity', {})
    
    def evaluate_position(self, data: List[Dict[str, Any]], index: int) -> Signal:
        """
        Evaluate current position for 5m exit conditions.
        
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
        
        # Check profit target
        if pnl_pct >= self.profit_target:
            reason = f'5m profit target: {pnl_pct:.2%}'
            if self.current_position.side == 'LONG':
                return Signal('CLOSE_LONG', 1.0, reason, {'pnl_pct': pnl_pct})
            else:
                return Signal('CLOSE_SHORT', 1.0, reason, {'pnl_pct': pnl_pct})
        
        # Check stop loss
        if pnl_pct <= -self.stop_loss:
            reason = f'5m stop loss: {pnl_pct:.2%}'
            if self.current_position.side == 'LONG':
                return Signal('CLOSE_LONG', 1.0, reason, {'pnl_pct': pnl_pct})
            else:
                return Signal('CLOSE_SHORT', 1.0, reason, {'pnl_pct': pnl_pct})
        
        # Check time-based exit
        hold_time = (current_time - entry_time).total_seconds()
        if hold_time >= self.max_hold_time:
            reason = f'5m time exit: {hold_time:.0f}s'
            if self.current_position.side == 'LONG':
                return Signal('CLOSE_LONG', 1.0, reason, {'hold_time': hold_time})
            else:
                return Signal('CLOSE_SHORT', 1.0, reason, {'hold_time': hold_time})
        
        return Signal('NONE', 0.0, 'Position held', {})
    
    def _momentum_prediction(self, indicators: Dict[str, Any]) -> float:
        """Momentum-based prediction for 5m."""
        momentum_score = (
            indicators['momentum_1m'] * 0.3 +
            indicators['momentum_3m'] * 0.25 +
            indicators['momentum_5m'] * 0.25 +
            indicators['momentum_10m'] * 0.15 +
            indicators['momentum_15m'] * 0.05
        )
        
        if momentum_score > self.momentum_threshold:
            return momentum_score * 8  # Adjusted scale for 5m
        elif momentum_score < -self.momentum_threshold:
            return -momentum_score * 8  # Adjusted scale for 5m
        else:
            return 0
    
    def _neural_network_prediction(self, indicators: Dict[str, Any]) -> float:
        """Neural network-based prediction for 5m."""
        # Simplified neural network
        inputs = [
            indicators['momentum_1m'],
            indicators['momentum_5m'],
            indicators['momentum_15m'],
            indicators['volume_ratio'],
            indicators['volatility'],
            indicators['price_position'],
            indicators['rsi_momentum'],
            indicators['acceleration'],
            indicators['trend_strength']
        ]
        
        # Normalize inputs
        normalized_inputs = [min(1.0, max(-1.0, x)) for x in inputs]
        
        # Simple weighted sum (simplified neural network)
        weights = [0.2, 0.2, 0.1, 0.15, 0.1, 0.1, 0.1, 0.05, 0.1]
        weighted_sum = sum(normalized_inputs[i] * weights[i] for i in range(len(normalized_inputs)))
        
        # Sigmoid activation
        output = 1.0 / (1.0 + math.exp(-weighted_sum * 6))  # Adjusted scale for 5m
        
        if output > 0.4:  # Higher threshold for 5m
            return output
        else:
            return -(1.0 - output) if output < 0.6 else 0
    
    def _ml_features_prediction(self, indicators: Dict[str, Any]) -> float:
        """Machine learning features prediction for 5m."""
        # Feature engineering
        features = {
            'momentum_score': self._calculate_momentum_score(indicators),
            'volume_score': self._calculate_volume_score(indicators),
            'volatility_score': self._calculate_volatility_score(indicators),
            'trend_score': self._calculate_trend_score(indicators),
            'acceleration_score': self._calculate_acceleration_score(indicators)
        }
        
        # Weighted ensemble
        score = (
            features['momentum_score'] * 0.4 +
            features['volume_score'] * 0.3 +
            features['volatility_score'] * 0.2 +
            features['trend_score'] * 0.1
        )
        
        if score > 0.4:  # Higher threshold for 5m
            return score
        else:
            return -score if score < -0.4 else 0
    
    def _volume_analysis_prediction(self, indicators: Dict[str, Any]) -> float:
        """Volume analysis prediction for 5m."""
        volume_score = min(1.0, indicators['volume_ratio'] / 1.3)  # Adjusted for 5m
        volume_momentum_score = min(1.0, abs(indicators['volume_momentum']) * 8)
        
        combined_score = (volume_score * 0.7 + volume_momentum_score * 0.3)
        
        if indicators['momentum_1m'] > 0:
            return combined_score
        else:
            return -combined_score
    
    def _calculate_momentum_score(self, indicators: Dict[str, Any]) -> float:
        """Calculate momentum score for 5m."""
        return min(1.0, abs(indicators['momentum_1m']) * 80)
    
    def _calculate_volume_score(self, indicators: Dict[str, Any]) -> float:
        """Calculate volume score for 5m."""
        if indicators['volume_ratio'] > 1.3:
            return 1.0
        elif indicators['volume_ratio'] > 1.15:
            return 0.8
        elif indicators['volume_ratio'] > 1.05:
            return 0.6
        else:
            return 0.3
    
    def _calculate_volatility_score(self, indicators: Dict[str, Any]) -> float:
        """Calculate volatility score for 5m."""
        if 0.002 <= indicators['volatility'] <= 0.015:
            return 1.0
        elif 0.001 <= indicators['volatility'] <= 0.025:
            return 0.7
        else:
            return 0.4
    
    def _calculate_trend_score(self, indicators: Dict[str, Any]) -> float:
        """Calculate trend score for 5m."""
        return min(1.0, abs(indicators['trend_strength']) * 800)
    
    def _calculate_acceleration_score(self, indicators: Dict[str, Any]) -> float:
        """Calculate acceleration score for 5m."""
        return min(1.0, abs(indicators['acceleration']) * 80)
    
    def _calculate_trend_strength(self, prices: List[float]) -> float:
        """Calculate trend strength using linear regression slope."""
        if len(prices) < 15:
            return 0.0
        
        n = len(prices)
        x = list(range(n))
        y = prices
        
        # Simple linear regression
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        return slope / prices[-1] if prices[-1] > 0 else 0.0
    
    def _detect_market_regime(self, volatility: float, volume_ratio: float, trend_strength: float) -> str:
        """Detect current market regime for 5m."""
        if abs(trend_strength) > 0.0008 and volume_ratio > 1.15:
            return 'trending'
        elif volatility < 0.001 and volume_ratio < 1.05:
            return 'ranging'
        else:
            return 'mixed'
    
    def _calculate_rsi_momentum(self, prices: List[float]) -> float:
        """Calculate RSI-like momentum indicator for 5m."""
        if len(prices) < 14:
            return 0.0
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(-change)
        
        avg_gain = sum(gains[-14:]) / 14
        avg_loss = sum(losses[-14:]) / 14
        
        if avg_loss == 0:
            return 1.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # Normalize to [-1, 1]
        return (rsi - 50) / 50
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get strategy-specific performance statistics."""
        return {
            'total_signals': self.total_signals,
            'executed_signals': self.executed_signals,
            'successful_trades': self.successful_trades,
            'strategy_type': 'Super Optimized 5m',
            'target_return': '3%+',
            'ensemble_weights': self.ensemble_weights
        }
