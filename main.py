"""Main application entry point for spyTrade."""
import logging
import time
from datetime import datetime
import json
from typing import Dict, List, Optional

from config import config
from data.fetchers import DataFetcher, MarketDataProcessor
from analysis import TechnicalAnalyzer
from alerts import SignalGenerator
from news import SentimentAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('spytrade.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SpyTradeApp:
    """Main application class for trade advice generation."""
    
    def __init__(self):
        """Initialize the application."""
        self.running = False
        self.signals_history = []
        
        logger.info("SpyTrade Application initialized")
    
    def run(self, once: bool = False):
        """
        Run the application.
        
        Args:
            once: If True, run once and exit. If False, run continuously.
        """
        logger.info("Starting SpyTrade application")
        self.running = True
        
        try:
            while self.running:
                self.analyze_all_symbols()
                
                if once:
                    break
                
                logger.info(f"Next update in {config.UPDATE_INTERVAL} seconds")
                time.sleep(config.UPDATE_INTERVAL)
        
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
        finally:
            self.stop()
    
    def analyze_all_symbols(self):
        """Analyze all configured symbols and generate signals."""
        logger.info(f"Analyzing symbols: {config.SYMBOLS}")
        
        for symbol in config.SYMBOLS:
            try:
                signal = self.analyze_symbol(symbol)
                
                if signal:
                    self.signals_history.append(signal)
                    self.print_signal(signal)
                    self.save_signal(signal)
            
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}", exc_info=True)
    
    def analyze_symbol(self, symbol: str) -> Optional[object]:
        """
        Analyze a single symbol and generate a trade signal.
        
        Args:
            symbol: Trading symbol (e.g., 'SPY', 'BTC-USD')
            
        Returns:
            TradeSignal object or None
        """
        logger.info(f"Analyzing {symbol}")
        
        # Fetch market data
        if symbol == 'BTC-USD' or symbol == 'BTC':
            candles = DataFetcher.fetch_crypto_data('BTC')
        else:
            candles = DataFetcher.fetch_stock_data_yfinance(symbol)
        
        if not candles:
            logger.warning(f"No data fetched for {symbol}")
            return None
        
        # Calculate technical indicators
        indicators = TechnicalAnalyzer.calculate_all_indicators(candles)
        
        # Fetch and analyze news
        news_articles = DataFetcher.fetch_news(symbol)
        sentiment_summary = SentimentAnalyzer.get_sentiment_summary(news_articles)
        news_sentiment = sentiment_summary.get('average_sentiment', 0.0)
        
        logger.info(f"{symbol} - News Sentiment: {news_sentiment:.2f} ({sentiment_summary.get('category')})")
        
        # Get price action analysis
        price_action = TechnicalAnalyzer.analyze_price_action(candles)
        
        # Generate signal
        signal = SignalGenerator.generate_signal(
            symbol=symbol,
            candles=candles,
            technical_indicators=indicators,
            news_sentiment=news_sentiment,
            atr_value=indicators.atr
        )
        
        return signal
    
    def print_signal(self, signal):
        """Print signal to console in a formatted way."""
        output = f"""
╔══════════════════════════════════════════════════════════════════╗
║                    TRADE SIGNAL GENERATED                        ║
╚══════════════════════════════════════════════════════════════════╝
Symbol:          {signal.symbol}
Signal Type:     {signal.signal_type}
Confidence:      {signal.confidence:.1f}%
Entry Price:     ${signal.entry_price:.2f}
Stop Loss:       ${signal.stop_loss:.2f}
Take Profit:     ${signal.take_profit:.2f}
Risk/Reward:     {(signal.take_profit - signal.entry_price) / (signal.entry_price - signal.stop_loss):.2f} : 1
Indicators:      {', '.join(signal.indicators_used)}
Reasoning:       {signal.reasoning}
Timestamp:       {signal.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
"""
        logger.info(output)
        print(output)
    
    def save_signal(self, signal):
        """Save signal to JSON file for historical tracking."""
        try:
            with open('signals_history.json', 'a') as f:
                f.write(json.dumps(signal.to_dict()) + '\n')
        except Exception as e:
            logger.error(f"Error saving signal: {e}")
    
    def stop(self):
        """Stop the application."""
        logger.info("Stopping SpyTrade application")
        self.running = False
    
    def get_latest_signals(self) -> List[Dict]:
        """Get latest signals for each symbol."""
        latest_signals = {}
        
        for signal in reversed(self.signals_history):
            if signal.symbol not in latest_signals:
                latest_signals[signal.symbol] = signal.to_dict()
        
        return list(latest_signals.values())

def main():
    """Main entry point."""
    app = SpyTradeApp()
    
    # Run continuously (comment out 'once=True' for production)
    app.run(once=False)

if __name__ == '__main__':
    main()
