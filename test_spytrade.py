"""Unit tests for spyTrade components."""
import unittest
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data import Candle, TechnicalIndicators, TradeSignal


class TestDataModels(unittest.TestCase):
    """Test data model classes."""
    
    def test_candle_creation(self):
        """Test Candle object creation."""
        candle = Candle(
            timestamp=datetime.now(),
            symbol='SPY',
            open=450.0,
            high=451.0,
            low=449.0,
            close=450.5,
            volume=1000000
        )
        
        self.assertEqual(candle.symbol, 'SPY')
        self.assertEqual(candle.close, 450.5)
        self.assertEqual(candle.volume, 1000000)
    
    def test_candle_to_dict(self):
        """Test Candle to_dict method."""
        candle = Candle(
            timestamp=datetime.now(),
            symbol='SPY',
            open=450.0,
            high=451.0,
            low=449.0,
            close=450.5,
            volume=1000000
        )
        
        candle_dict = candle.to_dict()
        self.assertEqual(candle_dict['symbol'], 'SPY')
        self.assertEqual(candle_dict['close'], 450.5)
    
    def test_technical_indicators_creation(self):
        """Test TechnicalIndicators object creation."""
        indicators = TechnicalIndicators(
            rsi=45.5,
            macd=0.25,
            sma_20=449.0,
            sma_50=448.0
        )
        
        self.assertEqual(indicators.rsi, 45.5)
        self.assertEqual(indicators.macd, 0.25)
        self.assertIsNone(indicators.atr)
    
    def test_trade_signal_creation(self):
        """Test TradeSignal object creation."""
        signal = TradeSignal(
            symbol='SPY',
            signal_type='BUY',
            confidence=75.5,
            entry_price=450.0,
            stop_loss=445.0,
            take_profit=460.0,
            reasoning='RSI oversold',
            indicators_used=['RSI', 'MACD'],
            timestamp=datetime.now()
        )
        
        self.assertEqual(signal.symbol, 'SPY')
        self.assertEqual(signal.signal_type, 'BUY')
        self.assertEqual(signal.confidence, 75.5)
    
    def test_trade_signal_to_dict(self):
        """Test TradeSignal to_dict method."""
        signal = TradeSignal(
            symbol='SPY',
            signal_type='BUY',
            confidence=75.5,
            entry_price=450.0,
            stop_loss=445.0,
            take_profit=460.0,
            reasoning='RSI oversold',
            indicators_used=['RSI', 'MACD'],
            timestamp=datetime.now()
        )
        
        signal_dict = signal.to_dict()
        self.assertEqual(signal_dict['symbol'], 'SPY')
        self.assertEqual(signal_dict['signal_type'], 'BUY')
        self.assertIsNotNone(signal_dict['timestamp'])


class TestTechnicalAnalysis(unittest.TestCase):
    """Test technical analysis calculations."""
    
    def setUp(self):
        """Set up test data."""
        from analysis import TechnicalAnalyzer
        self.analyzer = TechnicalAnalyzer
    
    def test_rsi_calculation(self):
        """Test RSI calculation."""
        # Create a simple uptrend
        prices = [100 + i * 0.5 for i in range(50)]
        
        rsi = self.analyzer.calculate_rsi(prices)
        
        self.assertIsNotNone(rsi)
        self.assertGreater(rsi, 0)
        self.assertLess(rsi, 100)
        # Uptrend should have high RSI
        self.assertGreater(rsi, 50)
    
    def test_rsi_insufficient_data(self):
        """Test RSI with insufficient data."""
        prices = [100, 101, 102]
        
        rsi = self.analyzer.calculate_rsi(prices, period=14)
        
        self.assertIsNone(rsi)
    
    def test_sma_calculation(self):
        """Test SMA calculation."""
        prices = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
        
        sma = self.analyzer.calculate_sma(prices, period=5)
        
        self.assertIsNotNone(sma)
        self.assertGreater(sma, 100)
        self.assertLess(sma, 110)
    
    def test_sma_insufficient_data(self):
        """Test SMA with insufficient data."""
        prices = [100, 101, 102]
        
        sma = self.analyzer.calculate_sma(prices, period=5)
        
        self.assertIsNone(sma)
    
    def test_bollinger_bands_calculation(self):
        """Test Bollinger Bands calculation."""
        prices = [100 + i * 0.1 for i in range(30)]
        
        upper, middle, lower = self.analyzer.calculate_bollinger_bands(prices, period=20)
        
        self.assertIsNotNone(upper)
        self.assertIsNotNone(middle)
        self.assertIsNotNone(lower)
        self.assertGreater(upper, middle)
        self.assertGreater(middle, lower)


class TestSignalGeneration(unittest.TestCase):
    """Test signal generation."""
    
    def setUp(self):
        """Set up test data."""
        from alerts import SignalGenerator
        self.generator = SignalGenerator
        from data import Candle
        
        # Create test candles
        self.test_candles = []
        for i in range(50):
            candle = Candle(
                timestamp=datetime.now(),
                symbol='SPY',
                open=450.0,
                high=451.0,
                low=449.0,
                close=450.0 + i * 0.1,
                volume=1000000
            )
            self.test_candles.append(candle)
    
    def test_signal_generation_insufficient_data(self):
        """Test signal generation with insufficient data."""
        from data import TechnicalIndicators
        
        signal = self.generator.generate_signal(
            symbol='SPY',
            candles=self.test_candles[:2],
            technical_indicators=TechnicalIndicators()
        )
        
        self.assertIsNone(signal)


if __name__ == '__main__':
    unittest.main()
