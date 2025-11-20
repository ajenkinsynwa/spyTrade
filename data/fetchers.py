"""Data fetching utilities for spyTrade."""
import yfinance as yf
from datetime import datetime
from typing import List, Optional
import logging

from data import Candle, TechnicalIndicators, MarketData

logger = logging.getLogger(__name__)


class DataFetcher:
    """Fetches stock and crypto market data."""

    @staticmethod
    def fetch_stock_data_yfinance(symbol: str) -> List[Candle]:
        """Fetch daily stock candles using yfinance."""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="6mo", interval="1d")

            candles = []
            for idx, row in hist.iterrows():
                candles.append(
                    Candle(
                        timestamp=idx.to_pydatetime(),
                        symbol=symbol,
                        open=float(row["Open"]),
                        high=float(row["High"]),
                        low=float(row["Low"]),
                        close=float(row["Close"]),
                        volume=int(row["Volume"]),
                    )
                )

            return candles

        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")
            return []

    @staticmethod
    def fetch_crypto_data(symbol: str = "BTC", fiat: str = "USD") -> List[Candle]:
        """Fetch crypto candles using yfinance."""
        try:
            ticker = yf.Ticker(f"{symbol}-{fiat}")
            hist = ticker.history(period="6mo", interval="1d")

            candles = []
            for idx, row in hist.iterrows():
                candles.append(
                    Candle(
                        timestamp=idx.to_pydatetime(),
                        symbol=f"{symbol}-{fiat}",
                        open=float(row["Open"]),
                        high=float(row["High"]),
                        low=float(row["Low"]),
                        close=float[row["Close"]],
                        volume=int(row.get("Volume", 0)),
                    )
                )

            return candles

        except Exception as e:
            logger.error(f"Error fetching crypto data for {symbol}: {e}")
            return []


class MarketDataProcessor:
    """Simple processors for candles."""

    @staticmethod
    def calculate_price_change(candles: List[Candle], lookback: int = 1) -> Optional[float]:
        """Percent price change across last N candles."""
        if len(candles) <= lookback:
            return None

        first = candles[-(lookback+1)].close
        last = candles[-1].close

        return ((last - first) / first) * 100 if first != 0 else None

    @staticmethod
    def calculate_volume_sma(candles: List[Candle], period: int = 20) -> Optional[float]:
        """Volume SMA."""
        if len(candles) < period:
            return None

        volumes = [c.volume for c in candles[-period:]]
        return sum(volumes) / period
