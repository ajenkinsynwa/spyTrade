"""Configuration module for API keys and settings."""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    
    # API Keys
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
    FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY', '')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
    
    # API Endpoints
    ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co/query'
    FINNHUB_BASE_URL = 'https://finnhub.io/api/v1'
    NEWS_API_BASE_URL = 'https://newsapi.org/v2'
    COINGECKO_BASE_URL = 'https://api.coingecko.com/api/v3'
    
    # Application Settings
    UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', 1800))  # 30 minutes
    SYMBOLS = os.getenv('SYMBOLS', 'SPY,BTC-USD').split(',')
    LOOKBACK_PERIOD = int(os.getenv('LOOKBACK_PERIOD', 100))
    
    # Technical Analysis Parameters
    RSI_PERIOD = 14
    RSI_OVERBOUGHT = 70
    RSI_OVERSOLD = 30
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    SMA_SHORT = 20
    SMA_LONG = 50
    
    # Risk Management
    DEFAULT_STOP_LOSS_PERCENT = 2.0
    DEFAULT_TAKE_PROFIT_PERCENT = 4.0
    
    # Signal Thresholds
    CONFIDENCE_THRESHOLD = 60  # Minimum confidence % for signals

config = Config()
