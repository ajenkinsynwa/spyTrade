"""Data fetching utilities for spyTrade."""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import ccxt
import pandas as pd
import requests
import yfinance as yf

from config import config

from data import Candle, TechnicalIndicators, MarketData

logger = logging.getLogger(__name__)


class DataFetcher:
    """Fetches stock and crypto market data."""

    @staticmethod
    def _candles_from_df(df: pd.DataFrame, symbol: str) -> List[Candle]:
        """Convert a DataFrame with OHLCV columns into Candle objects."""
        if df is None or df.empty:
            return []

        candles = []
        for idx, row in df.iterrows():
            timestamp = idx.to_pydatetime() if hasattr(idx, "to_pydatetime") else idx
            candles.append(
                Candle(
                    timestamp=timestamp,
                    symbol=symbol,
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=int(row.get("Volume", 0)),
                )
            )

        return candles

    @staticmethod
    def fetch_stock_data_yfinance(symbol: str) -> List[Candle]:
        """Fetch daily stock candles using yfinance."""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="6mo", interval="1d")

            candles = DataFetcher._candles_from_df(hist, symbol)
            if candles:
                return candles

            logger.warning("yfinance returned no data for %s; trying fallbacks", symbol)
            candles = DataFetcher.fetch_stock_data_alphavantage(symbol)
            if candles:
                return candles

            return DataFetcher.fetch_stock_data_stooq(symbol)

        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")
            return []

    @staticmethod
    def fetch_stock_data_intraday(symbol: str, interval_minutes: int = 30) -> List[Candle]:
        """Fetch intraday candles (default 30min) using Finnhub/Alpha Vantage/yfinance."""
        candles = DataFetcher.fetch_stock_data_finnhub(symbol, interval_minutes)
        if candles:
            return candles

        candles = DataFetcher.fetch_stock_data_alpha_intraday(symbol, interval_minutes)
        if candles:
            return candles

        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="60d", interval=f"{interval_minutes}m")
            candles = DataFetcher._candles_from_df(hist, symbol)
            if candles:
                return candles
        except Exception as e:
            logger.error("yfinance intraday fetch failed for %s: %s", symbol, e)

        return DataFetcher.fetch_stock_data_yfinance(symbol)

    @staticmethod
    def fetch_crypto_data(symbol: str = "BTC", fiat: str = "USD") -> List[Candle]:
        """Fetch crypto candles using yfinance."""
        try:
            ticker = yf.Ticker(f"{symbol}-{fiat}")
            hist = ticker.history(period="6mo", interval="1d")

            candles = DataFetcher._candles_from_df(hist, f"{symbol}-{fiat}")
            if candles:
                return candles

            logger.warning("yfinance returned no data for %s-%s; trying CoinGecko", symbol, fiat)
            return DataFetcher.fetch_crypto_data_coingecko(symbol, fiat)

        except Exception as e:
            logger.error(f"Error fetching crypto data for {symbol}: {e}")
            return []

    @staticmethod
    def fetch_crypto_data_intraday(symbol: str = "BTC", fiat: str = "USD", interval: str = "30m") -> List[Candle]:
        """Fetch intraday crypto candles using ccxt (Binance) with CoinGecko fallback."""
        markets_to_try = [f"{symbol}/{fiat.upper()}"]
        if fiat.upper() == "USD":
            markets_to_try.append(f"{symbol}/USDT")

        exchange_ids = ["binance", "kraken", "bitfinex", "bitstamp", "coinbase"]
        for exchange_id in exchange_ids:
            try:
                exchange = getattr(ccxt, exchange_id)({"enableRateLimit": True})
                if not exchange.has.get("fetchOHLCV"):
                    continue
                exchange.load_markets()
                if interval not in exchange.timeframes:
                    continue

                for market in markets_to_try:
                    if market not in exchange.symbols:
                        continue
                    ohlcv = exchange.fetch_ohlcv(market, timeframe=interval, limit=200)
                    if not ohlcv:
                        continue
                    candles = []
                    for ts_ms, open_p, high_p, low_p, close_p, volume in ohlcv:
                        candles.append(
                            Candle(
                                timestamp=datetime.fromtimestamp(ts_ms / 1000.0),
                                symbol=f"{symbol}-{fiat}",
                                open=float(open_p),
                                high=float(high_p),
                                low=float(low_p),
                                close=float(close_p),
                                volume=int(volume),
                            )
                        )
                    return candles
            except Exception as e:
                logger.error("ccxt intraday fetch failed for %s: %s", exchange_id, e)
                continue

        return DataFetcher.fetch_crypto_data_coingecko(symbol, fiat)

    @staticmethod
    def fetch_stock_data_alphavantage(symbol: str) -> List[Candle]:
        """Fetch daily stock candles using Alpha Vantage."""
        if not config.ALPHA_VANTAGE_API_KEY or config.ALPHA_VANTAGE_API_KEY == "demo":
            return []

        try:
            params = {
                "function": "TIME_SERIES_DAILY_ADJUSTED",
                "symbol": symbol,
                "outputsize": "compact",
                "apikey": config.ALPHA_VANTAGE_API_KEY,
            }
            response = requests.get(config.ALPHA_VANTAGE_BASE_URL, params=params, timeout=15)
            payload = response.json()
            series = payload.get("Time Series (Daily)", {})
            if not series:
                return []

            rows = []
            for date_str, row in series.items():
                rows.append(
                    {
                        "Date": date_str,
                        "Open": row.get("1. open"),
                        "High": row.get("2. high"),
                        "Low": row.get("3. low"),
                        "Close": row.get("4. close"),
                        "Volume": row.get("6. volume") or row.get("5. volume"),
                    }
                )

            df = pd.DataFrame(rows)
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.set_index("Date").sort_index()
            return DataFetcher._candles_from_df(df, symbol)
        except Exception as e:
            logger.error("Alpha Vantage fetch failed for %s: %s", symbol, e)
            return []

    @staticmethod
    def fetch_stock_data_alpha_intraday(symbol: str, interval_minutes: int = 30) -> List[Candle]:
        """Fetch intraday stock candles using Alpha Vantage."""
        if not config.ALPHA_VANTAGE_API_KEY or config.ALPHA_VANTAGE_API_KEY == "demo":
            return []

        try:
            params = {
                "function": "TIME_SERIES_INTRADAY",
                "symbol": symbol,
                "interval": f"{interval_minutes}min",
                "outputsize": "full",
                "apikey": config.ALPHA_VANTAGE_API_KEY,
            }
            response = requests.get(config.ALPHA_VANTAGE_BASE_URL, params=params, timeout=15)
            payload = response.json()
            key = f"Time Series ({interval_minutes}min)"
            series = payload.get(key, {})
            if not series:
                return []

            rows = []
            for date_str, row in series.items():
                rows.append(
                    {
                        "Date": date_str,
                        "Open": row.get("1. open"),
                        "High": row.get("2. high"),
                        "Low": row.get("3. low"),
                        "Close": row.get("4. close"),
                        "Volume": row.get("5. volume"),
                    }
                )

            df = pd.DataFrame(rows)
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.set_index("Date").sort_index()
            cutoff = datetime.utcnow() - timedelta(days=config.INTRADAY_LOOKBACK_DAYS)
            df = df[df.index >= cutoff]
            return DataFetcher._candles_from_df(df, symbol)
        except Exception as e:
            logger.error("Alpha Vantage intraday fetch failed for %s: %s", symbol, e)
            return []

    @staticmethod
    def fetch_stock_data_finnhub(symbol: str, interval_minutes: int = 30) -> List[Candle]:
        """Fetch intraday stock candles using Finnhub."""
        if not config.FINNHUB_API_KEY:
            return []

        try:
            end_ts = int(datetime.utcnow().timestamp())
            start_ts = int((datetime.utcnow() - timedelta(days=config.INTRADAY_LOOKBACK_DAYS)).timestamp())
            params = {
                "symbol": symbol,
                "resolution": str(interval_minutes),
                "from": start_ts,
                "to": end_ts,
                "token": config.FINNHUB_API_KEY,
            }
            resp = requests.get(f"{config.FINNHUB_BASE_URL}/stock/candle", params=params, timeout=15)
            data = resp.json()
            if data.get("s") != "ok":
                return []

            candles = []
            for ts, open_p, high_p, low_p, close_p, volume in zip(
                data.get("t", []),
                data.get("o", []),
                data.get("h", []),
                data.get("l", []),
                data.get("c", []),
                data.get("v", []),
            ):
                candles.append(
                    Candle(
                        timestamp=datetime.fromtimestamp(ts),
                        symbol=symbol,
                        open=float(open_p),
                        high=float(high_p),
                        low=float(low_p),
                        close=float(close_p),
                        volume=int(volume),
                    )
                )
            return candles
        except Exception as e:
            logger.error("Finnhub intraday fetch failed for %s: %s", symbol, e)
            return []

    @staticmethod
    def fetch_stock_data_stooq(symbol: str) -> List[Candle]:
        """Fetch daily stock candles from Stooq as a fallback."""
        stooq_symbol = symbol.lower()
        if "." not in stooq_symbol:
            stooq_symbol = f"{stooq_symbol}.us"

        url = f"https://stooq.com/q/d/l/?s={stooq_symbol}&i=d"
        try:
            df = pd.read_csv(url)
            if df.empty or "Date" not in df.columns:
                return []

            df["Date"] = pd.to_datetime(df["Date"])
            df = df.rename(
                columns={
                    "Open": "Open",
                    "High": "High",
                    "Low": "Low",
                    "Close": "Close",
                    "Volume": "Volume",
                }
            )
            df = df.set_index("Date").sort_index()
            cutoff = datetime.utcnow() - timedelta(days=180)
            df = df[df.index >= cutoff]
            return DataFetcher._candles_from_df(df, symbol)
        except Exception as e:
            logger.error("Stooq fetch failed for %s: %s", symbol, e)
            return []

    @staticmethod
    def fetch_crypto_data_coingecko(symbol: str = "BTC", fiat: str = "USD") -> List[Candle]:
        """Fetch daily crypto candles using CoinGecko OHLC."""
        coin_id = "bitcoin" if symbol.upper() == "BTC" else symbol.lower()
        vs_currency = fiat.lower()

        try:
            ohlc_url = f"{config.COINGECKO_BASE_URL}/coins/{coin_id}/ohlc"
            ohlc_resp = requests.get(
                ohlc_url,
                params={"vs_currency": vs_currency, "days": 365},
                timeout=15,
            )
            ohlc = ohlc_resp.json()
            if not isinstance(ohlc, list) or not ohlc:
                return []

            volume_url = f"{config.COINGECKO_BASE_URL}/coins/{coin_id}/market_chart"
            volume_resp = requests.get(
                volume_url,
                params={"vs_currency": vs_currency, "days": 365, "interval": "daily"},
                timeout=15,
            )
            volume_data = volume_resp.json().get("total_volumes", [])
            volume_map: Dict[int, float] = {int(ts): float(vol) for ts, vol in volume_data}

            candles = []
            for row in ohlc:
                ts_ms, open_p, high_p, low_p, close_p = row
                volume = volume_map.get(int(ts_ms), 0.0)
                candles.append(
                    Candle(
                        timestamp=datetime.fromtimestamp(ts_ms / 1000.0),
                        symbol=f"{symbol}-{fiat}",
                        open=float(open_p),
                        high=float(high_p),
                        low=float(low_p),
                        close=float(close_p),
                        volume=int(volume),
                    )
                )

            return candles
        except Exception as e:
            logger.error("CoinGecko fetch failed for %s-%s: %s", symbol, fiat, e)
            return []

    @staticmethod
    def fetch_news(symbol: str, limit: int = 10) -> List[Dict[str, str]]:
        """Fetch recent news for a symbol using Finnhub or NewsAPI."""
        symbol_upper = symbol.upper()
        keyword_pool = {
            "federal reserve", "fed", "rate hike", "rate cut", "interest rate",
            "inflation", "cpi", "jobs report", "nonfarm", "treasury", "yield",
            "recession", "gdp", "market", "stocks", "equities"
        }

        if symbol_upper in {"SPY", "SPX", "^GSPC"}:
            keyword_pool.update({"s&p 500", "spx", "spy", "s&p"})
        elif "BTC" in symbol_upper:
            keyword_pool.update({"bitcoin", "btc", "crypto", "cryptocurrency", "blockchain"})

        def matches_keywords(text: str) -> bool:
            text_lower = (text or "").lower()
            return any(keyword in text_lower for keyword in keyword_pool)

        def filter_articles(articles: List[Dict[str, str]]) -> List[Dict[str, str]]:
            filtered = []
            for item in articles:
                blob = f"{item.get('headline', '')} {item.get('content', '')}"
                if matches_keywords(blob):
                    filtered.append(item)
            return filtered[:limit]

        if config.FINNHUB_API_KEY:
            try:
                if symbol_upper in {"SPY", "SPX", "^GSPC"}:
                    params = {"category": "general", "token": config.FINNHUB_API_KEY}
                    resp = requests.get(f"{config.FINNHUB_BASE_URL}/news", params=params, timeout=15)
                    data = resp.json()
                elif "BTC" in symbol_upper:
                    params = {"category": "crypto", "token": config.FINNHUB_API_KEY}
                    resp = requests.get(f"{config.FINNHUB_BASE_URL}/news", params=params, timeout=15)
                    data = resp.json()
                else:
                    params = {"symbol": symbol, "token": config.FINNHUB_API_KEY}
                    resp = requests.get(f"{config.FINNHUB_BASE_URL}/company-news", params=params, timeout=15)
                    data = resp.json()

                articles = []
                for item in data:
                    articles.append(
                        {
                            "headline": item.get("headline", ""),
                            "content": item.get("summary", ""),
                            "url": item.get("url", ""),
                            "datetime": item.get("datetime"),
                        }
                    )
                filtered = filter_articles(articles)
                if filtered:
                    return filtered
            except Exception as e:
                logger.warning("Finnhub news fetch failed for %s: %s", symbol, e)

        if config.NEWS_API_KEY:
            try:
                if symbol_upper in {"SPY", "SPX", "^GSPC"}:
                    query = '"S&P 500" OR SPX OR SPY OR "Federal Reserve" OR "rate hike" OR "rate cut" OR inflation OR CPI'
                elif "BTC" in symbol_upper:
                    query = 'bitcoin OR btc OR cryptocurrency OR crypto OR blockchain OR "Bitcoin ETF"'
                else:
                    query = symbol
                params = {
                    "q": query,
                    "pageSize": limit,
                    "apiKey": config.NEWS_API_KEY,
                    "language": "en",
                    "sortBy": "publishedAt",
                }
                resp = requests.get(f"{config.NEWS_API_BASE_URL}/everything", params=params, timeout=15)
                data = resp.json().get("articles", [])
                articles = [
                    {
                        "headline": item.get("title", ""),
                        "content": item.get("description", ""),
                        "url": item.get("url", ""),
                        "datetime": item.get("publishedAt"),
                    }
                    for item in data
                ]
                filtered = filter_articles(articles)
                return filtered[:limit]
            except Exception as e:
                logger.warning("NewsAPI fetch failed for %s: %s", symbol, e)

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
