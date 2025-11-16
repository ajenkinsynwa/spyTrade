# spyTrade Developer Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Main Application                      │
│                   (main.py / example.py)                │
└────────────────┬────────────────────────────────────────┘
                 │
        ┌────────┼────────┬──────────────┬──────────┐
        ▼        ▼        ▼              ▼          ▼
    ┌───────┐ ┌──────┐ ┌────────┐   ┌────────┐  ┌──────┐
    │ Data  │ │Signal│ │Analysis│   │  News  │  │Config│
    │ Layer │ │ Gen  │ │ Layer  │   │ Analyst│  │ Layer│
    └───┬───┘ └──┬───┘ └────┬───┘   └────┬───┘  └──┬───┘
        │        │          │            │         │
    ┌───▼────────▼──────────▼────────────▼─────────▼──┐
    │         Free Market Data APIs                   │
    │ ┌─────────────┐  ┌──────────┐  ┌────────────┐ │
    │ │ yfinance    │  │ CoinGecko│  │ Finnhub    │ │
    │ │ (Stocks)    │  │ (Crypto) │  │ (News)     │ │
    │ └─────────────┘  └──────────┘  └────────────┘ │
    └──────────────────────────────────────────────────┘
```

## Module Breakdown

### 1. Data Layer (`data/`)

**Purpose**: Fetches and structures market data from various sources.

#### `fetchers.py`
- **`DataFetcher.fetch_stock_data_yfinance()`**: Fetches stock OHLCV data using yfinance
- **`DataFetcher.fetch_crypto_data()`**: Fetches crypto data from CoinGecko
- **`DataFetcher.fetch_news()`**: Fetches news from Finnhub or NewsAPI
- **`MarketDataProcessor`**: Converts candles to pandas DataFrames, calculates metrics

#### `__init__.py` (Data Models)
- **`Candle`**: Represents a single OHLCV bar
  - Fields: timestamp, symbol, open, high, low, close, volume
  - Methods: to_dict()

- **`TechnicalIndicators`**: Container for calculated indicators
  - Fields: rsi, macd, sma_20, sma_50, bollinger_*, atr
  - Methods: to_dict()

- **`MarketData`**: Complete market analysis data
  - Combines candles, indicators, volume, price changes

- **`TradeSignal`**: Final trade recommendation
  - Fields: symbol, signal_type, confidence, entry, stop_loss, take_profit, reasoning
  - Methods: to_dict()

### 2. Analysis Layer (`analysis/`)

**Purpose**: Performs technical analysis and identifies trading patterns.

#### `__init__.py` (Technical Analysis)
- **`TechnicalAnalyzer`**: All indicator calculations

**Key Methods:**
- `calculate_rsi()`: Relative Strength Index (momentum)
- `calculate_macd()`: MACD histogram and signal line
- `calculate_sma()`: Simple moving averages
- `calculate_bollinger_bands()`: Volatility bands
- `calculate_atr()`: Average True Range (volatility)
- `identify_resistance_support()`: Key price levels
- `analyze_price_action()`: Pattern recognition
- `calculate_all_indicators()`: Comprehensive analysis

**Price Action Analysis:**
- Doji, Hammer, Shooting Star patterns
- Trend direction (uptrend, downtrend, ranging)
- Close position within candle body
- Higher High/Low vs Lower High/Low

#### `ai_models.py` (Machine Learning)
- **`MLPredictor`**: Pattern recognition models
  - `predict_next_move()`: Trend prediction
  - `detect_support_resistance_clusters()`: Level clustering
  - `calculate_volatility_regime()`: Volatility classification
  - `identify_patterns()`: Candlestick pattern detection

### 3. Alert/Signal Generation (`alerts/`)

**Purpose**: Combines all analysis into actionable trade signals.

#### `__init__.py` (Signal Generation)
- **`SignalGenerator`**: Generates BUY/SELL/HOLD signals

**Scoring System (Weighted Average):**
```
Total Confidence = 
  RSI Score (20%) +
  MACD Score (20%) +
  Price Action Score (20%) +
  Moving Average Score (15%) +
  Bollinger Bands Score (10%) +
  News Sentiment Score (10%) +
  ML Prediction Score (5%)
```

**Signal Thresholds:**
- BUY: Confidence > 60%
- SELL: Confidence < 40%
- HOLD: 40% ≤ Confidence ≤ 60%

**Risk Management:**
- Stop Loss = Entry - (ATR × 1.5) for buys
- Take Profit = Entry + (ATR × 2.0) for buys
- Risk/Reward automatically calculated

### 4. Sentiment Analysis (`news/`)

**Purpose**: Analyzes sentiment from news and financial data.

#### `__init__.py` (Sentiment Analysis)
- **`SentimentAnalyzer`**: NLP-based sentiment detection

**Methods:**
- `analyze_article()`: Single article sentiment
- `analyze_articles()`: Multiple articles average
- `get_sentiment_summary()`: Comprehensive sentiment stats
- `categorize_sentiment()`: Convert score to label

**Analysis Approach:**
1. TextBlob sentiment analysis (70% weight)
   - Natural language processing
   - Polarity: -1 (negative) to +1 (positive)

2. Keyword-based analysis (30% weight)
   - Bullish keywords: surge, rally, positive, growth, etc.
   - Bearish keywords: crash, plunge, negative, loss, etc.

### 5. Configuration (`config/`)

**Purpose**: Centralized settings management.

#### `__init__.py`
- **API Keys**: Alpha Vantage, Finnhub, NewsAPI
- **API Endpoints**: Base URLs for services
- **Technical Parameters**: RSI, MACD, SMA periods
- **Risk Management**: Stop loss, take profit percentages
- **Signal Thresholds**: Minimum confidence for signals

## Development Workflow

### Adding a New Indicator

1. **Add calculation to `analysis/__init__.py`:**
```python
@staticmethod
def calculate_new_indicator(prices, period):
    """Calculate new indicator."""
    # Your calculation
    return value
```

2. **Update `calculate_all_indicators()`:**
```python
new_value = TechnicalAnalyzer.calculate_new_indicator(prices)
return TechnicalIndicators(
    # ... existing indicators ...
    new_indicator=new_value
)
```

3. **Add scoring to `SignalGenerator` in `alerts/__init__.py`:**
```python
@staticmethod
def _analyze_new_indicator(indicators, confidence_components, indicators_used):
    """Analyze new indicator. Returns score and updates lists."""
    if indicators.new_indicator is None:
        return 50
    
    indicators_used.append('New_Indicator')
    
    # Your scoring logic
    score = 50 + some_calculation(indicators.new_indicator)
    confidence_components.append(score)
    return float(score)
```

4. **Integrate into `generate_signal()`:**
```python
new_score = SignalGenerator._analyze_new_indicator(
    technical_indicators, confidence_components, indicators_used
)

# Add to weighted average calculation
```

### Adding a New Data Source

1. **Create fetcher method in `data/fetchers.py`:**
```python
@staticmethod
def fetch_new_source(symbol):
    """Fetch data from new source."""
    try:
        # Your API call
        # Convert to Candle objects
        return candles
    except Exception as e:
        logger.error(f"Error fetching from new source: {e}")
        return []
```

2. **Update `analyze_symbol()` in `main.py`:**
```python
if symbol == 'NEW_SYMBOL':
    candles = DataFetcher.fetch_new_source(symbol)
else:
    # existing code
```

### Testing

**Run unit tests:**
```bash
python -m pytest test_spytrade.py -v
```

**Run examples:**
```bash
python example.py
```

**Run main application (once):**
```bash
python main.py
```

## Performance Optimization

### Data Processing
- Use numpy for vectorized calculations
- Minimize API calls with caching
- Batch process multiple indicators

### API Rate Limiting
- Respect free tier limits
- Implement request queuing
- Add exponential backoff for retries

### Memory Management
- Only keep required historical data (100-200 candles)
- Clear old signals periodically
- Use generators for large datasets

## Extension Ideas

### 1. Advanced ML Models
```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

class AdvancedMLPredictor:
    def __init__(self):
        self.model = RandomForestClassifier()
    
    def train(self, X, y):
        self.model.fit(X, y)
    
    def predict(self, X):
        return self.model.predict(X)
```

### 2. Real-time WebSocket Data
```python
import websocket

class RealTimeDataFetcher:
    def __init__(self):
        self.ws = websocket.WebSocket()
    
    def start_stream(self, symbol):
        # WebSocket connection for real-time data
        pass
```

### 3. Backtesting Engine
```python
class Backtester:
    def __init__(self, initial_capital=10000):
        self.capital = initial_capital
        self.trades = []
    
    def backtest(self, signals, historical_data):
        # Simulate trading
        pass
```

### 4. Trading Bot Integration
```python
from ib_insync import IB, Stock, MarketOrder

class TradingBot:
    def __init__(self):
        self.ib = IB()
    
    def place_order(self, signal):
        # Execute trade via Interactive Brokers
        pass
```

## Common Issues & Solutions

### Issue: Slow Data Fetching
- **Cause**: Multiple sequential API calls
- **Solution**: Implement parallel fetching with threading/asyncio
- **Code**:
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    spy_future = executor.submit(DataFetcher.fetch_stock_data_yfinance, 'SPY')
    btc_future = executor.submit(DataFetcher.fetch_crypto_data, 'BTC')
```

### Issue: Inconsistent Indicator Values
- **Cause**: Different calculation methods or data normalization
- **Solution**: Use TA library for validation
- **Code**:
```python
import ta

df = MarketDataProcessor.candles_to_dataframe(candles)
ta_rsi = ta.momentum.rsi(df['close'])
our_rsi = TechnicalAnalyzer.calculate_rsi([c.close for c in candles])
# Compare values
```

### Issue: Memory Leak with Long-Running Process
- **Cause**: Growing signals_history list
- **Solution**: Implement periodic cleanup
- **Code**:
```python
def cleanup_old_signals(self, days=7):
    cutoff = datetime.now() - timedelta(days=days)
    self.signals_history = [s for s in self.signals_history 
                           if s.timestamp > cutoff]
```

## Style Guide

- Follow PEP 8 conventions
- Use type hints for function parameters
- Document all public methods with docstrings
- Use logging instead of print statements
- Keep functions focused and small (<50 lines)
- Test edge cases (empty data, None values)

## Code Structure Example

```python
"""Module description."""
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class MyAnalyzer:
    """Class description."""
    
    @staticmethod
    def analyze_data(data: List[float]) -> Optional[float]:
        """
        Analyze data and return result.
        
        Args:
            data: List of values to analyze
            
        Returns:
            Result value or None if insufficient data
        """
        if len(data) < 10:
            logger.warning("Insufficient data")
            return None
        
        # Your calculation
        result = sum(data) / len(data)
        
        return float(result)
```

## Deployment Considerations

1. **Environment Variables**: Use `.env` file for sensitive data
2. **Logging**: Rotate logs to prevent disk space issues
3. **Error Handling**: Graceful degradation when APIs fail
4. **Monitoring**: Track signal accuracy and API performance
5. **Scheduling**: Use cron or task schedulers for automated runs
6. **Notifications**: Add alerts via email/SMS/Telegram

---

For questions or contributions, feel free to reach out!
