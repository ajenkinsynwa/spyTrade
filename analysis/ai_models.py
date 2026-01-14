"""Optional AI/ML models for advanced predictions."""
import logging
import numpy as np
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

class MLPredictor:
    """
    Machine learning models for trade prediction.
    Provides simple pattern recognition and trend prediction.
    """
    
    @staticmethod
    def predict_next_move(prices: List[float], lookback: int = 20) -> Tuple[Optional[float], float]:
        """
        Predict whether price will go up or down.
        
        Args:
            prices: List of historical prices
            lookback: Number of candles to use for prediction
            
        Returns:
            Tuple of (prediction: -1 to 1, confidence: 0 to 1)
                prediction > 0 = bullish
                prediction < 0 = bearish
        """
        if len(prices) < lookback + 1:
            return None, 0.0
        
        recent_prices = prices[-lookback:]
        next_price = prices[-1]
        
        # Calculate trend
        trend = np.polyfit(range(len(recent_prices)), recent_prices, 1)[0]
        
        # Calculate volatility
        returns = np.diff(recent_prices) / recent_prices[:-1]
        volatility = np.std(returns)
        
        # Normalize trend to -1 to 1
        if volatility > 0:
            prediction = np.tanh(trend / volatility)
        else:
            prediction = 0.0
        
        # Confidence based on trend strength
        confidence = abs(trend) / (volatility + 0.0001) if volatility > 0 else 0.5
        confidence = min(confidence / 10, 1.0)  # Normalize to 0-1
        
        return float(prediction), float(confidence)

    @staticmethod
    def predict_with_features(
        candles: List,
        indicators,
        news_sentiment: Optional[float] = None,
        lookback: int = 20
    ) -> Tuple[Optional[float], float]:
        """
        Predict next move using price trend plus technical/sentiment features.

        Returns:
            Tuple of (prediction: -1 to 1, confidence: 0 to 1)
        """
        if not candles or len(candles) < max(lookback, 5):
            return None, 0.0

        def get_indicator(name: str) -> Optional[float]:
            if indicators is None:
                return None
            if hasattr(indicators, name):
                return getattr(indicators, name)
            if isinstance(indicators, dict):
                return indicators.get(name)
            return None

        prices = [c.close for c in candles]
        last_price = prices[-1]

        base_pred, base_conf = MLPredictor.predict_next_move(prices, lookback=lookback)

        features = []
        weights = []

        if base_pred is not None:
            features.append(base_pred)
            weights.append(0.35)

        rsi = get_indicator("rsi")
        if rsi is not None:
            features.append((rsi - 50.0) / 50.0)
            weights.append(0.15)

        macd_hist = get_indicator("macd_histogram")
        if macd_hist is None:
            macd = get_indicator("macd")
            macd_signal = get_indicator("macd_signal")
            if macd is not None and macd_signal is not None:
                macd_hist = macd - macd_signal
        if macd_hist is not None and last_price:
            features.append(float(np.tanh(macd_hist / max(last_price * 0.005, 1e-6))))
            weights.append(0.15)

        sma_20 = get_indicator("sma_20")
        sma_50 = get_indicator("sma_50")
        if sma_20 is not None and sma_50 is not None and last_price:
            ma_trend = 1.0 if sma_20 > sma_50 else -1.0
            price_vs_sma = (last_price - sma_20) / last_price
            features.append(float(np.tanh(price_vs_sma * 5.0)) + (0.2 * ma_trend))
            weights.append(0.15)

        volumes = [c.volume for c in candles[-20:]]
        if volumes and last_price:
            volume_sma = sum(volumes) / len(volumes)
            if volume_sma > 0:
                vol_spike = (volumes[-1] / volume_sma) - 1.0
                features.append(float(np.tanh(vol_spike)))
                weights.append(0.1)

        if news_sentiment is not None:
            features.append(float(np.tanh(news_sentiment)))
            weights.append(0.1)

        if not features:
            return None, 0.0

        total_weight = sum(weights)
        prediction = sum(f * w for f, w in zip(features, weights)) / total_weight
        prediction = float(max(min(prediction, 1.0), -1.0))

        confidence = min(1.0, (abs(prediction) * 0.8) + (len(features) / 6.0) * 0.2)
        if base_pred is not None:
            confidence = min(1.0, (confidence + base_conf) / 2.0)

        return prediction, float(confidence)
    
    @staticmethod
    def detect_support_resistance_clusters(prices: List[float], window: int = 10) -> Tuple[List[float], List[float]]:
        """
        Detect clusters of support and resistance using price levels.
        
        Args:
            prices: List of historical prices
            window: Window size for clustering
            
        Returns:
            Tuple of (resistance_levels, support_levels)
        """
        if len(prices) < window:
            return [], []
        
        recent_prices = prices[-window * 5:]
        
        # Find local maxima (resistance)
        resistances = []
        for i in range(1, len(recent_prices) - 1):
            if recent_prices[i] > recent_prices[i-1] and recent_prices[i] > recent_prices[i+1]:
                resistances.append(recent_prices[i])
        
        # Find local minima (support)
        supports = []
        for i in range(1, len(recent_prices) - 1):
            if recent_prices[i] < recent_prices[i-1] and recent_prices[i] < recent_prices[i+1]:
                supports.append(recent_prices[i])
        
        # Cluster nearby levels
        resistances = MLPredictor._cluster_levels(resistances)
        supports = MLPredictor._cluster_levels(supports)
        
        return sorted(resistances, reverse=True), sorted(supports)
    
    @staticmethod
    def _cluster_levels(levels: List[float], threshold_percent: float = 0.5) -> List[float]:
        """
        Cluster price levels that are close together.
        
        Args:
            levels: List of price levels
            threshold_percent: Percentage threshold for clustering
            
        Returns:
            Clustered price levels (averages)
        """
        if not levels:
            return []
        
        levels = sorted(levels)
        clusters = []
        current_cluster = [levels[0]]
        
        for level in levels[1:]:
            # Check if level is within threshold of last level in cluster
            threshold = current_cluster[-1] * (threshold_percent / 100)
            
            if abs(level - current_cluster[-1]) <= threshold:
                current_cluster.append(level)
            else:
                # Start new cluster
                clusters.append(np.mean(current_cluster))
                current_cluster = [level]
        
        # Don't forget the last cluster
        if current_cluster:
            clusters.append(np.mean(current_cluster))
        
        return clusters
    
    @staticmethod
    def calculate_volatility_regime(prices: List[float], period: int = 20) -> str:
        """
        Determine the volatility regime (Low, Medium, High).
        
        Args:
            prices: List of prices
            period: Period for volatility calculation
            
        Returns:
            Volatility regime: 'Low', 'Medium', or 'High'
        """
        if len(prices) < period:
            return 'Medium'
        
        recent_prices = np.array(prices[-period:])
        returns = np.diff(recent_prices) / recent_prices[:-1]
        volatility = np.std(returns) * 100  # Convert to percentage
        
        if volatility < 1.0:
            return 'Low'
        elif volatility < 2.5:
            return 'Medium'
        else:
            return 'High'
    
    @staticmethod
    def identify_patterns(candles: List) -> List[str]:
        """
        Identify specific candlestick patterns.
        
        Args:
            candles: List of Candle objects
            
        Returns:
            List of identified patterns
        """
        patterns = []
        
        if len(candles) < 3:
            return patterns
        
        last = candles[-1]
        prev = candles[-2]
        
        # Engulfing pattern
        if (last.close > last.open and prev.close < prev.open and
            last.open < prev.close and last.close > prev.open):
            patterns.append('bullish_engulfing')
        
        if (last.close < last.open and prev.close > prev.open and
            last.open > prev.close and last.close < prev.open):
            patterns.append('bearish_engulfing')
        
        # Inside bar pattern
        if (last.high < prev.high and last.low > prev.low):
            patterns.append('inside_bar')
        
        return patterns
