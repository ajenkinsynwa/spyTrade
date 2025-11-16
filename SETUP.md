# spyTrade - Setup & Usage Guide

## Quick Start

### 1. Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Free API keys from:
  - [Alpha Vantage](https://www.alphavantage.co/) - Stock data
  - [Finnhub](https://finnhub.io/) - News & sentiment
  - [NewsAPI](https://newsapi.org/) - General news (optional)

### 2. Installation

Clone and setup the repository:
```bash
cd /Users/alexjenkins/Desktop/spyTrade
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configuration

Copy the example environment file and add your API keys:
```bash
cp .env.example .env
```

Edit `.env` with your API keys:
```
ALPHA_VANTAGE_API_KEY=your_key_here
FINNHUB_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
```

### 4. Run the Application

For a single analysis:
```bash
python main.py
```

The application will:
1. Fetch the latest 100 candles of 30-minute data for SPY and BTC
2. Calculate all technical indicators (RSI, MACD, Moving Averages, Bollinger Bands)
3. Analyze price action patterns
4. Fetch and analyze recent news sentiment
5. Generate trade signals with entry, stop loss, and take profit levels
6. Save signals to `signals_history.json`
7. Output results to console and `spytrade.log`

## Project Architecture

### Data Layer (`data/`)
- **`fetchers.py`**: Fetches market data from free APIs
  - `yfinance` for stock data (no API key needed)
  - `CoinGecko` for crypto data (no API key needed)
  - `Finnhub` and `NewsAPI` for news

- **`__init__.py`**: Data models
  - `Candle`: OHLCV data
  - `TechnicalIndicators`: Indicator values
  - `TradeSignal`: Generated trade recommendations

### Analysis Layer (`analysis/`)
- **`__init__.py`**: Technical analysis calculations
  - RSI, MACD, SMA, Bollinger Bands
  - ATR (Average True Range)
  - Support/Resistance detection
  - Price action pattern recognition

- **`ai_models.py`**: Machine learning utilities
  - Trend prediction
  - Support/Resistance clustering
  - Volatility regime identification
  - Candlestick pattern detection

### Signal Generation (`alerts/`)
- **`__init__.py`**: `SignalGenerator` class
  - Combines 7 different indicators with weighted scoring
  - Calculates confidence levels (0-100%)
  - Determines optimal entry, stop loss, and take profit

### Sentiment Analysis (`news/`)
- **`__init__.py`**: `SentimentAnalyzer` class
  - TextBlob-based NLP analysis
  - Keyword-based sentiment detection
  - Article categorization
  - Comprehensive sentiment summaries

### Configuration (`config/`)
- **`__init__.py`**: Centralized configuration
  - API endpoints
  - Technical analysis parameters
  - Risk management settings
  - Signal thresholds

## Trade Signal Components

Each signal includes:

1. **Signal Type**
   - `BUY`: Bullish conditions (confidence > 60%)
   - `SELL`: Bearish conditions (confidence < 40%)
   - `HOLD`: Neutral or insufficient confidence

2. **Confidence Score (0-100%)**
   - Based on weighted combination of 7 indicators:
     - RSI (20% weight)
     - MACD (20% weight)
     - Price Action (20% weight)
     - Moving Averages (15% weight)
     - Bollinger Bands (10% weight)
     - News Sentiment (10% weight)
     - ML Prediction (5% weight)

3. **Price Levels**
   - **Entry Price**: Current market price
   - **Stop Loss**: Risk management level
   - **Take Profit**: Target profit level
   - **Risk/Reward Ratio**: Calculated for position sizing

## Technical Indicators Used

### Momentum
- **RSI (Relative Strength Index)**
  - Overbought: > 70
  - Oversold: < 30
  
- **MACD (Moving Average Convergence Divergence)**
  - Positive histogram = bullish
  - Negative histogram = bearish

### Trend
- **Simple Moving Averages (SMA)**
  - 20-period: Short-term trend
  - 50-period: Medium-term trend
  - Golden Cross: SMA 20 > SMA 50 (bullish)
  - Death Cross: SMA 20 < SMA 50 (bearish)

### Volatility
- **Bollinger Bands**
  - Expansion = increasing volatility
  - Contraction = decreasing volatility
  
- **ATR (Average True Range)**
  - Used for stop loss and take profit sizing

### Price Action
- Candlestick patterns (doji, hammer, shooting star)
- Trend direction (higher highs/lows vs lower highs/lows)
- Body vs wick analysis

## News Sentiment Analysis

The sentiment analyzer uses two methods:

1. **TextBlob Sentiment Analysis**
   - Natural language processing
   - Polarity scoring (-1 to 1)
   - Weight: 70%

2. **Keyword-Based Analysis**
   - Bullish keywords: surge, rally, positive, gains, strong, etc.
   - Bearish keywords: crash, plunge, negative, losses, weak, etc.
   - Weight: 30%

**Categories:**
- Very Bullish: > 0.5
- Bullish: 0.2 to 0.5
- Neutral: -0.2 to 0.2
- Bearish: -0.5 to -0.2
- Very Bearish: < -0.5

## Output Files

### signals_history.json
Contains all historical signals in JSON format:
```json
{
  "symbol": "SPY",
  "signal_type": "BUY",
  "confidence": 72.5,
  "entry_price": 450.25,
  "stop_loss": 441.50,
  "take_profit": 467.75,
  "risk_reward": 2.0,
  "indicators_used": ["RSI", "MACD", "MA", "BB"],
  "reasoning": "...",
  "timestamp": "2025-11-15T10:30:00"
}
```

### spytrade.log
Detailed application logs:
- Data fetch results
- Indicator calculations
- Signal generation details
- Error tracking

## Customization

### Modify Analysis Parameters

Edit `config/__init__.py`:

```python
# RSI settings
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# Moving averages
SMA_SHORT = 20
SMA_LONG = 50

# Risk management
DEFAULT_STOP_LOSS_PERCENT = 2.0
DEFAULT_TAKE_PROFIT_PERCENT = 4.0

# Signal generation
CONFIDENCE_THRESHOLD = 60  # Minimum confidence for signals
```

### Add Custom Indicators

Add new indicator calculations to `analysis/__init__.py`:

```python
@staticmethod
def calculate_custom_indicator(prices, period):
    # Your calculation here
    return value
```

Then integrate into `SignalGenerator`:

```python
@staticmethod
def _analyze_custom_indicator(indicators, confidence_components, indicators_used):
    # Your analysis here
    confidence_components.append(score)
    indicators_used.append('Custom_Indicator')
    return score
```

## API Rate Limits (Free Tier)

- **Alpha Vantage**: 5 calls/min, 500 calls/day
- **Finnhub**: 60 calls/min, 60 per second
- **CoinGecko**: 10-50 calls/min (no API key needed)
- **NewsAPI**: 100 calls/day (free tier)

**Recommendation**: Set `UPDATE_INTERVAL` to at least 1800 seconds (30 min) to stay within rate limits.

## Risk Disclaimer

**⚠️ IMPORTANT:**

This application is for educational and research purposes only. It does not constitute financial advice. 

- Always do your own research
- Never risk more than you can afford to lose
- Use proper position sizing and risk management
- Past performance does not guarantee future results
- Markets are unpredictable and highly risky

Use this tool to supplement your analysis, not replace professional financial advice.

## Troubleshooting

### Issue: "No data fetched for symbol"
- Check internet connection
- Verify API keys are correct
- Check API rate limits haven't been exceeded
- Verify symbol is valid (e.g., 'SPY' for stocks, 'BTC-USD' for crypto)

### Issue: "Import X could not be resolved"
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again
- Check Python version is 3.8+

### Issue: Signals not generating
- Verify confidence threshold (default: 60%)
- Check technical indicators are calculating properly
- Review detailed logs in `spytrade.log`

## Future Enhancements

- [ ] WebSocket support for real-time data
- [ ] Backtesting engine
- [ ] Advanced ML models (neural networks, ensemble methods)
- [ ] Options strategy analysis
- [ ] Multi-timeframe analysis
- [ ] Web dashboard for visualization
- [ ] Telegram/Email alert notifications
- [ ] Paper trading simulation
- [ ] Risk analytics and position sizing
- [ ] Integration with trading APIs (Interactive Brokers, etc.)

## Support & Contribution

For issues or feature requests, please create an issue or pull request.

## License

MIT License - See LICENSE file for details
