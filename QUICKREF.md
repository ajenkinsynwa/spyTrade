# spyTrade Quick Reference

## Installation (One-time setup)

```bash
cd /Users/alexjenkins/Desktop/spyTrade
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your API keys
```

## Running the Application

### Single Analysis (Testing)
```bash
python main.py
```

### Continuous Monitoring (Production)
Edit `main.py` and change `app.run(once=False)` to `app.run(once=False)`, then:
```bash
nohup python main.py > spytrade.log 2>&1 &
```

### Run Examples
```bash
python example.py
```

### Run Tests
```bash
python -m pytest test_spytrade.py -v
```

## Understanding Signals

### Signal Types
- **BUY** (Bullish): Confidence > 60%
  - Consider entering long positions
  - Check Risk/Reward ratio
  
- **SELL** (Bearish): Confidence < 40%
  - Consider entering short positions
  - Or exit existing long positions
  
- **HOLD** (Neutral): 40% ≤ Confidence ≤ 60%
  - Wait for clearer signals
  - Monitor for direction change

### Key Metrics

| Metric | Meaning | Usage |
|--------|---------|-------|
| Confidence | Signal strength (0-100%) | Higher = more reliable |
| Entry Price | Current market price | Starting point for trade |
| Stop Loss | Maximum acceptable loss | Set tight for risk control |
| Take Profit | Target profit level | Plan exit before entry |
| Risk/Reward | TP distance / SL distance | Higher ratio = better trade setup |
| RSI | Momentum indicator | >70 overbought, <30 oversold |
| MACD | Trend + momentum | Histogram >0 bullish, <0 bearish |
| SMA 20/50 | Trend direction | 20 > 50 uptrend, 20 < 50 downtrend |

## Configuration Quick Edit

Edit `config/__init__.py` to customize:

```python
# Change RSI sensitivity
RSI_PERIOD = 14  # Default: 14
RSI_OVERBOUGHT = 70  # Default: 70
RSI_OVERSOLD = 30  # Default: 30

# Change moving averages
SMA_SHORT = 20  # Default: 20
SMA_LONG = 50  # Default: 50

# Change update interval (seconds)
UPDATE_INTERVAL = 1800  # 30 minutes - MUST be at least this to respect API limits

# Change minimum signal confidence
CONFIDENCE_THRESHOLD = 60  # Default: 60% - Higher = fewer but better signals

# Add more symbols
SYMBOLS = ['SPY', 'BTC-USD', 'QQQ', 'IWM']  # Default: SPY, BTC-USD
```

## Free API Keys Setup

### Alpha Vantage (Stock Data)
1. Go to: https://www.alphavantage.co/
2. Click "GET FREE API KEY"
3. Enter email and receive key
4. Free tier: 5 calls/min, 500/day
5. Add to `.env`: `ALPHA_VANTAGE_API_KEY=your_key`

### Finnhub (Stock News)
1. Go to: https://finnhub.io/
2. Sign up for free account
3. Copy API key from dashboard
4. Free tier: 60 calls/min
5. Add to `.env`: `FINNHUB_API_KEY=your_key`

### NewsAPI (General News)
1. Go to: https://newsapi.org/
2. Click "Get API Key"
3. Complete form and receive key
4. Free tier: 100 calls/day
5. Add to `.env`: `NEWS_API_KEY=your_key`

### CoinGecko (Crypto Data)
- **No API key required!**
- Completely free, no registration needed
- Unlimited calls (rate limited to 10-50/min)

## Output Files

### signals_history.json
```json
{
  "symbol": "SPY",
  "signal_type": "BUY",
  "confidence": 72.5,
  "entry_price": 450.25,
  "stop_loss": 441.50,
  "take_profit": 467.75,
  "risk_reward": 2.0,
  "indicators_used": ["RSI", "MACD", "MA", "Price_Action"],
  "reasoning": "...",
  "timestamp": "2025-11-15T10:30:00"
}
```

### spytrade.log
Application logs with:
- Data fetch results
- Indicator values
- Signal generation details
- Errors and warnings

## Troubleshooting

### "No data fetched"
```bash
# Check internet connection
ping www.google.com

# Check API key validity
# Visit https://www.alphavantage.co/ and verify key

# Check rate limits
# Wait 60+ seconds between requests for free tier
```

### "Import X could not be resolved"
```bash
# Verify venv is activated
source venv/bin/activate

# Reinstall packages
pip install -r requirements.txt

# Check Python version
python --version  # Must be 3.8+
```

### "signals_history.json permission denied"
```bash
# Fix permissions
chmod 644 signals_history.json

# Or create new file
rm signals_history.json
touch signals_history.json
```

## Using Individual Components

### Just Fetch Data
```python
from data.fetchers import DataFetcher

spy_data = DataFetcher.fetch_stock_data_yfinance('SPY')
btc_data = DataFetcher.fetch_crypto_data('BTC')
```

### Just Technical Analysis
```python
from analysis import TechnicalAnalyzer

indicators = TechnicalAnalyzer.calculate_all_indicators(candles)
print(f"RSI: {indicators.rsi}")
print(f"MACD: {indicators.macd}")
```

### Just Sentiment Analysis
```python
from news import SentimentAnalyzer
from data.fetchers import DataFetcher

news = DataFetcher.fetch_news('SPY')
sentiment = SentimentAnalyzer.get_sentiment_summary(news)
print(f"Sentiment: {sentiment['category']}")
```

### Just Signal Generation
```python
from alerts import SignalGenerator

signal = SignalGenerator.generate_signal(
    symbol='SPY',
    candles=candles,
    technical_indicators=indicators
)
print(f"Signal: {signal.signal_type} @ {signal.confidence:.1f}%")
```

## Common Workflows

### Analyze SPY Daily
```python
import time
from main import SpyTradeApp

app = SpyTradeApp()
while True:
    app.analyze_symbol('SPY')
    time.sleep(1800)  # 30 minutes
```

### Analyze Multiple Symbols
```bash
# Edit config/__init__.py
SYMBOLS = ['SPY', 'QQQ', 'IWM', 'BTC-USD']

# Run normally
python main.py
```

### Get Historical Signals
```python
import json

signals = []
with open('signals_history.json', 'r') as f:
    for line in f:
        signals.append(json.loads(line))

# Filter by symbol
spy_signals = [s for s in signals if s['symbol'] == 'SPY']

# Calculate win rate
wins = sum(1 for s in spy_signals if s['signal_type'] == 'BUY')
print(f"Generated {len(spy_signals)} signals, {wins} were bullish")
```

## Performance Tips

1. **Reduce API calls**: Increase `UPDATE_INTERVAL` to 3600+ seconds
2. **Faster processing**: Use fewer indicators or increase `LOOKBACK_PERIOD`
3. **Less data**: Reduce symbols in `SYMBOLS` config
4. **Background running**: Use `nohup` or systemd service
5. **Monitor logs**: Check `spytrade.log` for errors

## Risk Management

⚠️ **Remember:**
- This is for analysis/research only
- Never risk money you can't afford to lose
- Always use stop losses
- Start with paper trading
- Backtest strategies before live trading
- Markets can be unpredictable

## Next Steps

1. ✅ Get API keys (see above)
2. ✅ Set up application (see Installation)
3. ✅ Run example: `python example.py`
4. ✅ Analyze single symbol: `python main.py`
5. ✅ Review signals in `signals_history.json`
6. 📈 Backtest signals against historical prices
7. 🤖 Consider adding custom indicators
8. 📊 Create visualization dashboard
9. 🔔 Set up alerts/notifications
10. 💰 Paper trade with a broker

---

**Last Updated**: November 15, 2025
**Questions?** See SETUP.md or DEVELOPMENT.md for detailed guides
