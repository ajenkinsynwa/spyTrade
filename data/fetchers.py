"""Data fetching from various free APIs."""
import requests
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
from typing import List, Optional
import logging

from config import config
from data import Candle, MarketData, TechnicalIndicators

logger = logging.getLogger(__name__)

class DataFetcher:
    """Fetches market data from free APIs."""
    
    @staticmethod
    def fetch_stock_data_yfinance(symbol: str, period: str = '100d', interval: str = '1d') -> List[Candle]:
        """
        Fetch stock data using yfinance (free, no API key needed).
        Falls back to Alpha Vantage if yfinance fails.
        
        Args:
            symbol: Stock symbol (e.g., 'SPY')
            period: Period to fetch ('100d', '5d', etc.)
            interval: Candle interval ('1d' for daily, '1h' for hourly)
            
        Returns:
            List of Candle objects
        """
        try:
            data = yf.download(symbol, period=period, interval=interval, progress=False)
            candles = []
            
            # Check if data is empty
            if data is None or data.empty:
                logger.warning(f"yfinance returned no data for {symbol}, trying Alpha Vantage")
                return DataFetcher.fetch_stock_data_alpha_vantage(symbol)
            
            for timestamp, row in data.iterrows():
                candle = Candle(
                    timestamp=timestamp.to_pydatetime(),
                    symbol=symbol,
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=int(row['Volume'])
                )
                candles.append(candle)
            
            logger.info(f"Fetched {len(candles)} candles for {symbol}")
            return candles
        except Exception as e:
            logger.warning(f"yfinance failed for {symbol}, trying Alpha Vantage: {e}")
            # Fallback to Alpha Vantage
            return DataFetcher.fetch_stock_data_alpha_vantage(symbol)

    @staticmethod
    def fetch_stock_data_alpha_vantage(symbol: str) -> List[Candle]:
        """
        Fetch stock data using Alpha Vantage API.
        
        Args:
            symbol: Stock symbol (e.g., 'SPY')
            
        Returns:
            List of Candle objects
        """
        try:
            url = config.ALPHA_VANTAGE_BASE_URL
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'apikey': config.ALPHA_VANTAGE_API_KEY,
                'outputsize': 'full'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'Error Message' in data:
                logger.error(f"Alpha Vantage error: {data['Error Message']}")
                return []
            
            if 'Note' in data:
                logger.warning(f"Alpha Vantage rate limit: {data['Note']}")
                return []
            
            time_series = data.get('Time Series (Daily)', {})
            candles = []
            
            # Sort dates in ascending order and limit to last 100
            dates = sorted(time_series.keys())[-100:]
            
            for date_str in dates:
                row = time_series[date_str]
                candle = Candle(
                    timestamp=datetime.strptime(date_str, '%Y-%m-%d'),
                    symbol=symbol,
                    open=float(row['1. open']),
                    high=float(row['2. high']),
                    low=float(row['3. low']),
                    close=float(row['4. close']),
                    volume=int(float(row['5. volume']))
                )
                candles.append(candle)
            
            logger.info(f"Fetched {len(candles)} candles for {symbol} from Alpha Vantage")
            return candles
        except Exception as e:
            logger.error(f"Error fetching data from Alpha Vantage for {symbol}: {e}")
            return []

    @staticmethod
    def fetch_crypto_data(symbol: str = 'BTC', days: int = 100) -> List[Candle]:
        """
        Fetch cryptocurrency data from CoinGecko (free, no API key needed).
        
        Args:
            symbol: Crypto symbol ('BTC', 'ETH')
            days: Number of days to fetch
            
        Returns:
            List of Candle objects
        """
        try:
            # CoinGecko API for historical data
            url = 'https://api.coingecko.com/api/v3/coins'
            
            if symbol.upper() == 'BTC':
                coin_id = 'bitcoin'
            elif symbol.upper() == 'ETH':
                coin_id = 'ethereum'
            else:
                coin_id = symbol.lower()
            
            # Fetch market chart data
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'daily'
            }
            
            response = requests.get(
                f'{url}/{coin_id}/market_chart',
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            candles = []
            prices = data.get('prices', [])
            volumes = data.get('volumes', [])
            
            for i, (timestamp, price) in enumerate(prices):
                if i < len(volumes):
                    volume = volumes[i][1]
                else:
                    volume = 0
                
                dt = datetime.fromtimestamp(timestamp / 1000)
                
                candle = Candle(
                    timestamp=dt,
                    symbol=symbol,
                    open=float(price),
                    high=float(price),
                    low=float(price),
                    close=float(price),
                    volume=int(volume)
                )
                candles.append(candle)
            
            logger.info(f"Fetched {len(candles)} candles for {symbol}")
            return candles
        except Exception as e:
            logger.error(f"Error fetching crypto data for {symbol}: {e}")
            return []

    @staticmethod
    def fetch_news(symbol: str, limit: int = 10) -> List[dict]:
        """
        Fetch news for a symbol using NewsAPI or Finnhub.
        
        Args:
            symbol: Stock symbol
            limit: Number of articles to fetch
            
        Returns:
            List of news articles
        """
        news_items = []
        
        # Try Finnhub first if API key is available
        if config.FINNHUB_API_KEY:
            try:
                url = f'{config.FINNHUB_BASE_URL}/company-news'
                params = {
                    'symbol': symbol,
                    'token': config.FINNHUB_API_KEY
                }
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                articles = response.json()[:limit]
                
                for article in articles:
                    news_items.append({
                        'headline': article.get('headline', ''),
                        'source': article.get('source', ''),
                        'timestamp': article.get('datetime', ''),
                        'url': article.get('url', ''),
                        'sentiment': 'neutral'  # Will be analyzed separately
                    })
                
                logger.info(f"Fetched {len(news_items)} news items for {symbol} from Finnhub")
            except Exception as e:
                logger.error(f"Error fetching news from Finnhub: {e}")
        
        # Fallback to NewsAPI
        if not news_items and config.NEWS_API_KEY:
            try:
                url = f'{config.NEWS_API_BASE_URL}/everything'
                params = {
                    'q': symbol,
                    'apiKey': config.NEWS_API_KEY,
                    'pageSize': limit,
                    'sortBy': 'publishedAt'
                }
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                articles = response.json().get('articles', [])
                
                for article in articles:
                    news_items.append({
                        'headline': article.get('title', ''),
                        'source': article.get('source', {}).get('name', ''),
                        'timestamp': article.get('publishedAt', ''),
                        'url': article.get('url', ''),
                        'sentiment': 'neutral'
                    })
                
                logger.info(f"Fetched {len(news_items)} news items for {symbol} from NewsAPI")
            except Exception as e:
                logger.error(f"Error fetching news from NewsAPI: {e}")
        
        return news_items

class MarketDataProcessor:
    """Processes raw market data."""
    
    @staticmethod
    def candles_to_dataframe(candles: List[Candle]) -> pd.DataFrame:
        """Convert list of candles to pandas DataFrame."""
        if not candles:
            return pd.DataFrame()
        
        data = {
            'timestamp': [c.timestamp for c in candles],
            'open': [c.open for c in candles],
            'high': [c.high for c in candles],
            'low': [c.low for c in candles],
            'close': [c.close for c in candles],
            'volume': [c.volume for c in candles]
        }
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        return df
    
    @staticmethod
    def calculate_price_change(candles: List[Candle]) -> Optional[float]:
        """Calculate percentage change from first to last candle."""
        if len(candles) < 2:
            return None
        
        first_close = candles[0].close
        last_close = candles[-1].close
        
        return ((last_close - first_close) / first_close) * 100
    
    @staticmethod
    def calculate_volume_sma(candles: List[Candle], period: int = 20) -> Optional[float]:
        """Calculate simple moving average of volume."""
        if len(candles) < period:
            return None
        
        volumes = [c.volume for c in candles[-period:]]
        return sum(volumes) / len(volumes)
