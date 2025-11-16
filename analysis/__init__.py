"""Technical analysis indicators and calculations."""
import pandas as pd
import numpy as np
from typing import List, Tuple, Optional
import logging

from data import Candle, TechnicalIndicators

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """Performs technical analysis on market data."""
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
        """
        Calculate Relative Strength Index (RSI).
        
        Args:
            prices: List of close prices
            period: RSI period (default 14)
            
        Returns:
            RSI value (0-100) or None if insufficient data
        """
        if len(prices) < period + 1:
            return None
        
        prices = np.array(prices)
        deltas = np.diff(prices)
        
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100 if avg_gain > 0 else 50
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi)
    
    @staticmethod
    def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            prices: List of close prices
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period
            
        Returns:
            Tuple of (MACD, Signal, Histogram) or (None, None, None) if insufficient data
        """
        if len(prices) < slow:
            return None, None, None
        
        prices = np.array(prices, dtype=float)
        
        ema_fast = TechnicalAnalyzer._ema(prices, fast)
        ema_slow = TechnicalAnalyzer._ema(prices, slow)
        
        macd_line = ema_fast - ema_slow
        
        if len(macd_line) < signal:
            return None, None, None
        
        signal_line = TechnicalAnalyzer._ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return float(macd_line[-1]), float(signal_line[-1]), float(histogram[-1])
    
    @staticmethod
    def calculate_sma(prices: List[float], period: int) -> Optional[float]:
        """
        Calculate Simple Moving Average.
        
        Args:
            prices: List of prices
            period: SMA period
            
        Returns:
            SMA value or None if insufficient data
        """
        if len(prices) < period:
            return None
        
        return float(np.mean(prices[-period:]))
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """
        Calculate Bollinger Bands.
        
        Args:
            prices: List of close prices
            period: BB period
            std_dev: Standard deviation multiplier
            
        Returns:
            Tuple of (Upper, Middle, Lower) or (None, None, None)
        """
        if len(prices) < period:
            return None, None, None
        
        prices = np.array(prices[-period:], dtype=float)
        middle = np.mean(prices)
        std = np.std(prices)
        
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return float(upper), float(middle), float(lower)
    
    @staticmethod
    def calculate_atr(candles: List[Candle], period: int = 14) -> Optional[float]:
        """
        Calculate Average True Range.
        
        Args:
            candles: List of Candle objects
            period: ATR period
            
        Returns:
            ATR value or None if insufficient data
        """
        if len(candles) < period + 1:
            return None
        
        true_ranges = []
        
        for i in range(1, len(candles)):
            high = candles[i].high
            low = candles[i].low
            prev_close = candles[i-1].close
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)
        
        atr = np.mean(true_ranges[-period:])
        return float(atr)
    
    @staticmethod
    def identify_resistance_support(candles: List[Candle], lookback: int = 50) -> Tuple[Optional[float], Optional[float]]:
        """
        Identify recent resistance and support levels.
        
        Args:
            candles: List of Candle objects
            lookback: Number of candles to analyze
            
        Returns:
            Tuple of (Resistance, Support) levels
        """
        if len(candles) < lookback:
            lookback = len(candles)
        
        recent_candles = candles[-lookback:]
        
        highs = [c.high for c in recent_candles]
        lows = [c.low for c in recent_candles]
        
        # Find local extremes
        resistance = max(highs)
        support = min(lows)
        
        # Find recent swing highs and lows
        recent_high = max(c.high for c in recent_candles[-20:]) if len(recent_candles) >= 20 else resistance
        recent_low = min(c.low for c in recent_candles[-20:]) if len(recent_candles) >= 20 else support
        
        return float(resistance), float(support)
    
    @staticmethod
    def analyze_price_action(candles: List[Candle]) -> dict:
        """
        Analyze price action patterns.
        
        Args:
            candles: List of Candle objects
            
        Returns:
            Dictionary with price action analysis
        """
        if len(candles) < 3:
            return {}
        
        last_candle = candles[-1]
        prev_candle = candles[-2]
        prev_prev_candle = candles[-3]
        
        body_size = abs(last_candle.close - last_candle.open)
        total_range = last_candle.high - last_candle.low
        body_percent = (body_size / total_range * 100) if total_range > 0 else 0
        
        is_bullish = last_candle.close > last_candle.open
        is_bearish = last_candle.close < last_candle.open
        
        # Detect specific patterns
        patterns = []
        
        # Doji (small body, long wicks)
        if body_percent < 10 and total_range > body_size * 2:
            patterns.append('doji')
        
        # Hammer (small body, long lower wick)
        lower_wick = last_candle.open - last_candle.low if is_bullish else last_candle.close - last_candle.low
        if body_percent < 20 and lower_wick > body_size * 2:
            patterns.append('hammer')
        
        # Shooting star (small body, long upper wick)
        upper_wick = last_candle.high - last_candle.open if is_bearish else last_candle.high - last_candle.close
        if body_percent < 20 and upper_wick > body_size * 2:
            patterns.append('shooting_star')
        
        # Strong candle (large body, small wicks)
        if body_percent > 70:
            patterns.append('strong_candle')
        
        # Check for higher high/low or lower high/low
        higher_high = last_candle.high > prev_candle.high
        higher_low = last_candle.low > prev_candle.low
        lower_high = last_candle.high < prev_candle.high
        lower_low = last_candle.low < prev_candle.low
        
        trend_type = None
        if higher_high and higher_low:
            trend_type = 'uptrend'
        elif lower_high and lower_low:
            trend_type = 'downtrend'
        else:
            trend_type = 'ranging'
        
        return {
            'is_bullish': is_bullish,
            'is_bearish': is_bearish,
            'body_percent': body_percent,
            'patterns': patterns,
            'trend_type': trend_type,
            'close_position': (last_candle.close - last_candle.low) / total_range if total_range > 0 else 0.5
        }
    
    @staticmethod
    def _ema(prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate Exponential Moving Average."""
        if len(prices) < period:
            return np.array([])
        
        k = 2 / (period + 1)
        ema = np.zeros_like(prices)
        ema[0] = np.mean(prices[:period])
        
        for i in range(1, len(prices)):
            ema[i] = prices[i] * k + ema[i-1] * (1 - k)
        
        return ema
    
    @staticmethod
    def calculate_all_indicators(candles: List[Candle]) -> TechnicalIndicators:
        """
        Calculate all technical indicators for given candles.
        
        Args:
            candles: List of Candle objects
            
        Returns:
            TechnicalIndicators object
        """
        if not candles:
            return TechnicalIndicators()
        
        prices = [c.close for c in candles]
        
        # Calculate indicators
        rsi = TechnicalAnalyzer.calculate_rsi(prices)
        macd, macd_signal, macd_hist = TechnicalAnalyzer.calculate_macd(prices)
        sma_20 = TechnicalAnalyzer.calculate_sma(prices, 20)
        sma_50 = TechnicalAnalyzer.calculate_sma(prices, 50)
        bb_upper, bb_middle, bb_lower = TechnicalAnalyzer.calculate_bollinger_bands(prices)
        atr = TechnicalAnalyzer.calculate_atr(candles)
        
        return TechnicalIndicators(
            rsi=rsi,
            macd=macd,
            macd_signal=macd_signal,
            macd_histogram=macd_hist,
            sma_20=sma_20,
            sma_50=sma_50,
            bollinger_upper=bb_upper,
            bollinger_middle=bb_middle,
            bollinger_lower=bb_lower,
            atr=atr
        )
