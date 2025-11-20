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
        Generate a trade signal based on AI prediction as primary driver with technical confirmation.
        
        AI-FIRST APPROACH:
        - AI Prediction: 50% weight (primary decision maker)
        - Technical Indicators: 35% weight (confirmation)
        - News Sentiment: 15% weight (market context)
        
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
        price_action = TechnicalAnalyzer.analyze_price_action(candles)
        indicators_used = []
        
        # PRIMARY: AI PREDICTION (50% weight) - This is the main decision
        ai_score = SignalGenerator._analyze_ml_prediction(ml_prediction, indicators_used)
        
        # SECONDARY: Technical Indicators as CONFIRMATION (35% weight)
        rsi_score = SignalGenerator._analyze_rsi(technical_indicators, indicators_used)
        macd_score = SignalGenerator._analyze_macd(technical_indicators, indicators_used)
        ma_score = SignalGenerator._analyze_moving_averages(last_candle.close, technical_indicators, indicators_used)
        bb_score = SignalGenerator._analyze_bollinger_bands(last_candle.close, technical_indicators, indicators_used)
        pa_score = SignalGenerator._analyze_price_action(price_action, indicators_used)
        
        # TERTIARY: News Sentiment (15% weight) - Market context
        news_score = SignalGenerator._analyze_news_sentiment(news_sentiment, indicators_used)
        
        # Calculate weighted confidence with AI as PRIMARY
        # AI: 50%, Technical Avg: 35%, News: 15%
        technical_avg = (rsi_score + macd_score + ma_score + bb_score + pa_score) / 5
        total_confidence = (ai_score * 0.50) + (technical_avg * 0.35) + (news_score * 0.15)
        
        # Determine signal type based on AI prediction
        signal_type = SignalGenerator._determine_signal_type_ai_first(ai_score, technical_avg, news_score)
        
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
        reasoning = SignalGenerator._create_reasoning_ai_first(
            signal_type,
            ai_score,
            technical_avg,
            news_score,
            rsi_score,
            macd_score,
            ma_score,
            price_action
        )
        
        # Lower threshold for signals since AI is driving it
        if total_confidence < 35:  # Lowered from 40
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
    def _analyze_rsi(indicators, indicators_used) -> float:
        """Analyze RSI indicator. Returns score 0-100."""
        if indicators.rsi is None:
            return 50
        
        indicators_used.append('RSI')
        rsi = indicators.rsi
        
        if rsi < config.RSI_OVERSOLD:
            return 75  # Strong buy signal
        elif rsi < 40:
            return 60  # Moderate buy signal
        elif rsi > config.RSI_OVERBOUGHT:
            return 25  # Strong sell signal
        elif rsi > 60:
            return 40  # Moderate sell signal
        else:
            return 50  # Neutral
    
    @staticmethod
    def _analyze_macd(indicators, indicators_used) -> float:
        """Analyze MACD indicator. Returns score 0-100."""
        if indicators.macd is None or indicators.macd_signal is None:
            return 50
        
        indicators_used.append('MACD')
        
        # Positive histogram = bullish, negative = bearish
        histogram = indicators.macd_histogram or (indicators.macd - indicators.macd_signal)
        
        if histogram > 0 and indicators.macd > indicators.macd_signal:
            return 65
        elif histogram < 0 and indicators.macd < indicators.macd_signal:
            return 35
        else:
            return 50
    
    @staticmethod
    def _analyze_price_action(price_action, indicators_used) -> float:
        """Analyze price action patterns. Returns score 0-100."""
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
        
        return float(score)
    
    @staticmethod
    def _analyze_moving_averages(current_price, indicators, indicators_used) -> float:
        """Analyze moving average positions. Returns score 0-100."""
        if indicators.sma_20 is None or indicators.sma_50 is None:
            return 50
        
        indicators_used.append('MA')
        
        sma_20 = indicators.sma_20
        sma_50 = indicators.sma_50
        
        # Golden cross / death cross
        if sma_20 > sma_50:
            score = 60
        elif sma_20 < sma_50:
            score = 40
        else:
            score = 50
        
        # Price position relative to MAs
        if current_price > sma_20 > sma_50:
            score += 10
        elif current_price < sma_20 < sma_50:
            score -= 10
        
        return float(score)
    
    @staticmethod
    def _analyze_bollinger_bands(current_price, indicators, indicators_used) -> float:
        """Analyze Bollinger Bands positions. Returns score 0-100."""
        if indicators.bollinger_upper is None or indicators.bollinger_lower is None:
            return 50
        
        indicators_used.append('BB')
        
        upper = indicators.bollinger_upper
        lower = indicators.bollinger_lower
        middle = indicators.bollinger_middle or ((upper + lower) / 2)
        
        total_range = upper - lower
        position = (current_price - lower) / total_range if total_range > 0 else 0.5
        
        if position > 0.8:  # Near upper band
            return 35
        elif position < 0.2:  # Near lower band
            return 65
        else:
            return 50
    
    @staticmethod
    def _analyze_news_sentiment(sentiment_score, indicators_used) -> float:
        """Analyze news sentiment. Returns score 0-100."""
        if sentiment_score is None:
            return 50
        
        indicators_used.append('News_Sentiment')
        
        # Convert sentiment (-1 to 1) to confidence (0-100)
        score = 50 + (sentiment_score * 25)
        return float(score)
    
    @staticmethod
    def _analyze_ml_prediction(prediction, indicators_used) -> float:
        """Analyze ML model prediction. Returns score 0-100."""
        if prediction is None:
            return 50
        
        indicators_used.append('AI_Prediction')
        
        # Convert prediction (-1 to 1) to confidence (0-100)
        score = 50 + (prediction * 25)
        return float(score)
    
    @staticmethod
    def _determine_signal_type_ai_first(ai_score, technical_score, news_score) -> str:
        """
        Determine BUY, SELL, or HOLD based on AI as primary driver.
        
        AI Score > 60: Strong BUY signal from AI
        AI Score < 40: Strong SELL signal from AI  
        AI Score 40-60: HOLD (AI neutral)
        
        Technical indicators confirm or weaken the signal.
        """
        # AI is the primary driver
        if ai_score > 60:
            # AI says BUY - check if technicals agree or are neutral
            if technical_score > 50:
                return 'BUY'  # AI + Tech agree
            elif technical_score < 40:
                return 'HOLD'  # AI bullish but tech bearish = HOLD
            else:
                return 'BUY'  # AI bullish, tech neutral = BUY
                
        elif ai_score < 40:
            # AI says SELL - check if technicals agree or are neutral
            if technical_score < 50:
                return 'SELL'  # AI + Tech agree
            elif technical_score > 60:
                return 'HOLD'  # AI bearish but tech bullish = HOLD
            else:
                return 'SELL'  # AI bearish, tech neutral = SELL
                
        else:
            # AI is neutral (40-60) - use technicals
            if technical_score > 60:
                return 'BUY'
            elif technical_score < 40:
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
        else:  # HOLD
            # For HOLD, set SL at 2% below entry
            return entry * 0.98
    
    @staticmethod
    def _calculate_take_profit(entry, signal_type, atr) -> float:
        """Calculate take profit level."""
        atr_multiplier = 2.0
        
        if signal_type == 'BUY':
            return entry + (atr * atr_multiplier)
        elif signal_type == 'SELL':
            return entry - (atr * atr_multiplier)
        else:  # HOLD
            # For HOLD, set TP at 2% above entry
            return entry * 1.02
    
    @staticmethod
    def _create_reasoning_ai_first(signal_type, ai_score, technical_score, news_score, 
                                   rsi_score, macd_score, ma_score, price_action) -> str:
        """Create human-readable reasoning for AI-first signal."""
        parts = []
        
        # Main signal
        if signal_type == 'BUY':
            parts.append("🚀 BUY Signal")
        elif signal_type == 'SELL':
            parts.append("🔴 SELL Signal")
        else:
            parts.append("⏸️  HOLD - Neutral")
        
        # AI Analysis
        parts.append(f"AI: {ai_score:.1f}% {'(Bullish)' if ai_score > 60 else '(Bearish)' if ai_score < 40 else '(Neutral)'}")
        
        # Technical Confirmation
        parts.append(f"Technicals: {technical_score:.1f}%")
        
        # Sentiment
        if news_score > 55:
            parts.append(f"Sentiment: Bullish ({news_score:.1f}%)")
        elif news_score < 45:
            parts.append(f"Sentiment: Bearish ({news_score:.1f}%)")
        else:
            parts.append(f"Sentiment: Neutral ({news_score:.1f}%)")
        
        # Key indicators
        parts.append(f"RSI:{rsi_score:.0f} MACD:{macd_score:.0f} MA:{ma_score:.0f}")
        
        # Trend
        if price_action.get('trend_type'):
            parts.append(f"Trend: {price_action['trend_type'].upper()}")
        
        return " | ".join(parts)
