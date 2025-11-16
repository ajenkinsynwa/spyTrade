"""Signal generation and analysis."""
import logging
from datetime import datetime
from typing import Optional

from config import config
from data import TradeSignal
from analysis import TechnicalAnalyzer

logger = logging.getLogger(__name__)

class SignalGenerator:
    """Generates trade signals based on technical analysis and AI insights."""
    
    @staticmethod
    def generate_signal(
        symbol: str,
        candles: list,
        technical_indicators: dict,
        news_sentiment: Optional[float] = None,
        ml_prediction: Optional[float] = None,
        atr_value: Optional[float] = None
    ) -> Optional[TradeSignal]:
        """
        Generate a trade signal based on multiple factors.
        
        Args:
            symbol: Trading symbol
            candles: List of Candle objects
            technical_indicators: TechnicalIndicators object
            news_sentiment: News sentiment score (-1 to 1)
            ml_prediction: ML model prediction (-1 to 1)
            atr_value: Average True Range value
            
        Returns:
            TradeSignal object or None
        """
        if not candles or len(candles) < 5:
            return None
        
        last_candle = candles[-1]
        entry_price = last_candle.close
        
        # Calculate confidence score (0-100)
        confidence_components = []
        indicators_used = []
        
        # 1. RSI Analysis (weight: 20%)
        rsi_score = SignalGenerator._analyze_rsi(technical_indicators, confidence_components, indicators_used)
        
        # 2. MACD Analysis (weight: 20%)
        macd_score = SignalGenerator._analyze_macd(technical_indicators, confidence_components, indicators_used)
        
        # 3. Price Action Analysis (weight: 20%)
        price_action = TechnicalAnalyzer.analyze_price_action(candles)
        pa_score = SignalGenerator._analyze_price_action(price_action, confidence_components, indicators_used)
        
        # 4. Moving Average Analysis (weight: 15%)
        ma_score = SignalGenerator._analyze_moving_averages(
            last_candle.close,
            technical_indicators,
            confidence_components,
            indicators_used
        )
        
        # 5. Bollinger Bands Analysis (weight: 10%)
        bb_score = SignalGenerator._analyze_bollinger_bands(
            last_candle.close,
            technical_indicators,
            confidence_components,
            indicators_used
        )
        
        # 6. News Sentiment (weight: 10%)
        news_score = SignalGenerator._analyze_news_sentiment(news_sentiment, confidence_components, indicators_used)
        
        # 7. ML Prediction (weight: 5%)
        ml_score = SignalGenerator._analyze_ml_prediction(ml_prediction, confidence_components, indicators_used)
        
        # Calculate weighted average confidence
        total_confidence = sum(confidence_components) / len(confidence_components) if confidence_components else 50
        
        # Determine signal type
        signal_type = SignalGenerator._determine_signal_type(
            rsi_score, macd_score, pa_score, ma_score, bb_score, news_score, ml_score
        )
        
        # Determine risk parameters
        if atr_value is None:
            atr_value = technical_indicators.atr or (last_candle.high - last_candle.low)
        
        stop_loss = SignalGenerator._calculate_stop_loss(
            entry_price,
            signal_type,
            atr_value,
            price_action
        )
        
        take_profit = SignalGenerator._calculate_take_profit(
            entry_price,
            signal_type,
            atr_value
        )
        
        # Create reasoning string
        reasoning = SignalGenerator._create_reasoning(
            signal_type,
            rsi_score,
            macd_score,
            pa_score,
            ma_score,
            bb_score,
            news_score,
            ml_score,
            price_action
        )
        
        # Only return signal if confidence meets threshold
        if total_confidence < config.CONFIDENCE_THRESHOLD:
            return None
        
        signal = TradeSignal(
            symbol=symbol,
            signal_type=signal_type,
            confidence=total_confidence,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            reasoning=reasoning,
            indicators_used=indicators_used,
            timestamp=datetime.now()
        )
        
        return signal
    
    @staticmethod
    def _analyze_rsi(indicators, confidence_components, indicators_used) -> float:
        """Analyze RSI indicator. Returns score and updates lists."""
        if indicators.rsi is None:
            return 50
        
        indicators_used.append('RSI')
        rsi = indicators.rsi
        
        if rsi < config.RSI_OVERSOLD:
            confidence_components.append(75)  # Strong buy signal
            return 75
        elif rsi < 40:
            confidence_components.append(60)  # Moderate buy signal
            return 60
        elif rsi > config.RSI_OVERBOUGHT:
            confidence_components.append(25)  # Strong sell signal
            return 25
        elif rsi > 60:
            confidence_components.append(40)  # Moderate sell signal
            return 40
        else:
            confidence_components.append(50)  # Neutral
            return 50
    
    @staticmethod
    def _analyze_macd(indicators, confidence_components, indicators_used) -> float:
        """Analyze MACD indicator. Returns score and updates lists."""
        if indicators.macd is None or indicators.macd_signal is None:
            return 50
        
        indicators_used.append('MACD')
        
        # Positive histogram = bullish, negative = bearish
        histogram = indicators.macd_histogram or (indicators.macd - indicators.macd_signal)
        
        if histogram > 0 and indicators.macd > indicators.macd_signal:
            confidence_components.append(65)
            return 65
        elif histogram < 0 and indicators.macd < indicators.macd_signal:
            confidence_components.append(35)
            return 35
        else:
            confidence_components.append(50)
            return 50
    
    @staticmethod
    def _analyze_price_action(price_action, confidence_components, indicators_used) -> float:
        """Analyze price action patterns."""
        if not price_action:
            return 50
        
        indicators_used.append('Price_Action')
        score = 50
        
        if price_action.get('is_bullish'):
            score += 10
        if price_action.get('is_bearish'):
            score -= 10
        
        # Pattern analysis
        patterns = price_action.get('patterns', [])
        if 'strong_candle' in patterns and price_action.get('is_bullish'):
            score += 15
        elif 'strong_candle' in patterns and price_action.get('is_bearish'):
            score -= 15
        
        if 'hammer' in patterns:
            score += 10
        if 'shooting_star' in patterns:
            score -= 10
        
        # Trend analysis
        if price_action.get('trend_type') == 'uptrend':
            score += 10
        elif price_action.get('trend_type') == 'downtrend':
            score -= 10
        
        confidence_components.append(score)
        return float(score)
    
    @staticmethod
    def _analyze_moving_averages(current_price, indicators, confidence_components, indicators_used) -> float:
        """Analyze moving average positions."""
        if indicators.sma_20 is None or indicators.sma_50 is None:
            return 50
        
        indicators_used.append('MA')
        
        sma_20 = indicators.sma_20
        sma_50 = indicators.sma_50
        
        # Golden cross / death cross
        if sma_20 > sma_50:
            confidence_components.append(60)
            score = 60
        elif sma_20 < sma_50:
            confidence_components.append(40)
            score = 40
        else:
            confidence_components.append(50)
            score = 50
        
        # Price position relative to MAs
        if current_price > sma_20 > sma_50:
            score += 10
        elif current_price < sma_20 < sma_50:
            score -= 10
        
        return float(score)
    
    @staticmethod
    def _analyze_bollinger_bands(current_price, indicators, confidence_components, indicators_used) -> float:
        """Analyze Bollinger Bands positions."""
        if indicators.bollinger_upper is None or indicators.bollinger_lower is None:
            return 50
        
        indicators_used.append('BB')
        
        upper = indicators.bollinger_upper
        lower = indicators.bollinger_lower
        middle = indicators.bollinger_middle or ((upper + lower) / 2)
        
        total_range = upper - lower
        position = (current_price - lower) / total_range if total_range > 0 else 0.5
        
        if position > 0.8:  # Near upper band
            confidence_components.append(35)
            return 35
        elif position < 0.2:  # Near lower band
            confidence_components.append(65)
            return 65
        else:
            confidence_components.append(50)
            return 50
    
    @staticmethod
    def _analyze_news_sentiment(sentiment_score, confidence_components, indicators_used) -> float:
        """Analyze news sentiment."""
        if sentiment_score is None:
            return 50
        
        indicators_used.append('News_Sentiment')
        
        # Convert sentiment (-1 to 1) to confidence (0-100)
        score = 50 + (sentiment_score * 25)
        confidence_components.append(score)
        return float(score)
    
    @staticmethod
    def _analyze_ml_prediction(prediction, confidence_components, indicators_used) -> float:
        """Analyze ML model prediction."""
        if prediction is None:
            return 50
        
        indicators_used.append('ML_Prediction')
        
        # Convert prediction (-1 to 1) to confidence (0-100)
        score = 50 + (prediction * 25)
        confidence_components.append(score)
        return float(score)
    
    @staticmethod
    def _determine_signal_type(rsi, macd, pa, ma, bb, news, ml) -> str:
        """Determine BUY, SELL, or HOLD based on component scores."""
        scores = [rsi, macd, pa, ma, bb, news, ml]
        avg_score = sum(scores) / len(scores)
        
        if avg_score > 60:
            return 'BUY'
        elif avg_score < 40:
            return 'SELL'
        else:
            return 'HOLD'
    
    @staticmethod
    def _calculate_stop_loss(entry, signal_type, atr, price_action) -> float:
        """Calculate stop loss level."""
        atr_multiplier = 1.5 if price_action.get('trend_type') == 'uptrend' else 1.0
        
        if signal_type == 'BUY':
            return entry - (atr * atr_multiplier)
        elif signal_type == 'SELL':
            return entry + (atr * atr_multiplier)
        else:
            return entry
    
    @staticmethod
    def _calculate_take_profit(entry, signal_type, atr) -> float:
        """Calculate take profit level."""
        atr_multiplier = 2.0
        
        if signal_type == 'BUY':
            return entry + (atr * atr_multiplier)
        elif signal_type == 'SELL':
            return entry - (atr * atr_multiplier)
        else:
            return entry
    
    @staticmethod
    def _create_reasoning(signal_type, rsi, macd, pa, ma, bb, news, ml, price_action) -> str:
        """Create human-readable reasoning for the signal."""
        parts = []
        
        if signal_type == 'BUY':
            parts.append(f"Buy Signal - {signal_type}")
        elif signal_type == 'SELL':
            parts.append(f"Sell Signal - {signal_type}")
        else:
            parts.append("Hold - Neutral Conditions")
        
        parts.append(f"RSI: {rsi:.1f}, MACD: {macd:.1f}, Price Action: {pa:.1f}, MA: {ma:.1f}")
        
        if price_action.get('trend_type'):
            parts.append(f"Trend: {price_action['trend_type']}")
        
        if price_action.get('patterns'):
            parts.append(f"Patterns: {', '.join(price_action['patterns'])}")
        
        return " | ".join(parts)
