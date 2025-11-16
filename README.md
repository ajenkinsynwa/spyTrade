# spyTrade - Real-Time Trade Advice Application

A modern, real-time trading advice application with a TradingView-style dashboard. Analyzes S&P 500 (SPY) and Bitcoin on 30-minute timeframes using AI, technical analysis, and free market data APIs.

## ✨ Features

### 📊 Modern Web Dashboard
- **Interactive Charts**: Real-time candlestick charts with technical overlays
- **Live Indicators**: RSI, MACD, Moving Averages, Bollinger Bands, ATR
- **Trade Signals**: BUY/SELL/HOLD with confidence scores
- **Price Levels**: Entry, stop loss, take profit calculations
- **Risk/Reward Analysis**: Automatic position sizing recommendations
- **News Sentiment**: Real-time sentiment analysis from financial news
- **Multi-Symbol Support**: SPY, Bitcoin, and extensible to other assets

### 📈 Real-time Data Collection
- Price data from free APIs (yfinance, CoinGecko)
- Live trade volume analysis
- Market news integration (Finnhub, NewsAPI)
- 30-minute candlestick data

### 🔍 Technical Analysis
- Resistance and support area identification
- Price action pattern recognition
- 7 synchronized technical indicators
- Volume-weighted analysis
- Candlestick pattern detection

### 🤖 AI-Powered Insights
- Machine learning trend prediction
- Historical pattern recognition
- Sentiment analysis from news feeds
- Support/resistance clustering
- Volatility regime classification

### 🎯 Intelligent Trade Signals
- Weighted multi-indicator scoring system
- Confidence-based recommendations
- Automatic entry/exit levels
- Risk management guidelines

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/ajenkinsynwa/spyTrade.git
cd spyTrade

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env and add your free API keys
```

### Run Dashboard

```bash
# Start the web dashboard (opens in browser automatically)
python dashboard.py
```

The dashboard will be available at `http://localhost:5000`

### Run Command Line

```bash
# Run once
python main.py

# Run continuously
python main.py  # Edit main.py to change loop behavior
```

### Run Examples

```bash
# See individual component examples
python example.py
```

## Dashboard Features

### 📊 Interactive Charts
- Real-time candlestick charts with 30-min candles
- Technical indicator overlays (SMA 20, SMA 50)
- Volume analysis with color-coded bars
- Responsive zoom and pan controls
- Mobile-friendly design

### 🎯 Trade Signals
- **BUY**: Bullish conditions (Confidence > 60%)
- **SELL**: Bearish conditions (Confidence < 40%)  
- **HOLD**: Neutral or mixed signals
- Confidence percentage (0-100%)
- Automatic entry, stop loss, take profit levels
- Risk/reward ratio calculation

### 📈 Technical Indicators (Real-time)
- RSI (Relative Strength Index) - Momentum
- MACD (Moving Average Convergence Divergence) - Trend
- SMA 20 & 50 (Simple Moving Averages) - Trend Direction
- ATR (Average True Range) - Volatility
- Bollinger Bands - Volatility Bands

### 📰 News Sentiment
- Real-time sentiment analysis
- Bullish/Bearish/Neutral categorization
- Article count breakdown
- NLP + keyword-based analysis

### 💱 Multi-Symbol Support
Select from:
- SPY (S&P 500)
- BTC-USD (Bitcoin)
- Easily extensible to more symbols

## Project Structure

```
spyTrade/
├── app.py                    # Flask web server
├── dashboard.py              # Dashboard launcher
├── main.py                   # Command-line application
├── example.py                # Component examples
├── test_spytrade.py          # Unit tests
│
├── config/
│   └── __init__.py          # API keys and settings
│
├── data/
│   ├── __init__.py          # Data models (Candle, Signal, etc)
│   └── fetchers.py          # Data fetching from APIs
│
├── analysis/
│   ├── __init__.py          # Technical analysis (indicators)
│   └── ai_models.py         # ML models and pattern detection
│
├── alerts/
│   └── __init__.py          # Trade signal generation
│
├── news/
│   └── __init__.py          # Sentiment analysis
│
├── templates/
│   └── index.html           # Dashboard UI
│
├── requirements.txt         # Python dependencies
├── .env.example             # API key template
├── README.md                # This file
├── SETUP.md                 # Detailed setup guide
├── DASHBOARD.md             # Dashboard documentation
├── DEVELOPMENT.md           # Developer guide
└── QUICKREF.md              # Quick reference card
```

## Technical Indicators

### Momentum
- **RSI (14)**: 0-100 scale, >70 overbought, <30 oversold
- **MACD**: Trend confirmation, histogram shows momentum

### Trend  
- **SMA 20**: Short-term trend (blue line on chart)
- **SMA 50**: Medium-term trend
- Golden Cross: SMA 20 > 50 (bullish)
- Death Cross: SMA 20 < 50 (bearish)

### Volatility
- **Bollinger Bands**: Price inside bands = normal, outside = extreme
- **ATR**: Used for stop loss/take profit sizing

### Price Action
- Candlestick patterns (doji, hammer, shooting star)
- Trend structure (higher highs/lows vs lower highs/lows)
- Support/resistance levels

## Signal Components

Each trade signal includes:
- **Signal Type**: BUY, SELL, or HOLD
- **Confidence Score**: 0-100% (higher = more reliable)
- **Entry Price**: Current market price
- **Stop Loss**: Maximum acceptable loss level
- **Take Profit**: Target profit level
- **Risk/Reward Ratio**: Trade quality metric
- **Indicators Used**: Which indicators triggered the signal
- **Reasoning**: Human-readable explanation

## Scoring System

Signals use weighted multi-indicator analysis:
- RSI (20% weight) - Momentum
- MACD (20% weight) - Trend + Momentum
- Price Action (20% weight) - Chart patterns
- Moving Averages (15% weight) - Trend direction
- Bollinger Bands (10% weight) - Volatility
- News Sentiment (10% weight) - Market sentiment
- ML Prediction (5% weight) - Pattern prediction

## Getting Free API Keys

1. **Alpha Vantage** (Stock Data)
   - Visit: https://www.alphavantage.co/
   - Free tier: 5 calls/min, 500/day
   - Get key from email after signup

2. **Finnhub** (Stock News)
   - Visit: https://finnhub.io/
   - Free tier: 60 calls/min
   - Copy API key from dashboard

3. **NewsAPI** (General News - Optional)
   - Visit: https://newsapi.org/
   - Free tier: 100 calls/day
   - Get key from email signup

4. **CoinGecko** (Crypto Data)
   - NO API KEY REQUIRED!
   - Unlimited free access
   - No registration needed

## Documentation

- **[SETUP.md](SETUP.md)** - Detailed installation and configuration
- **[DASHBOARD.md](DASHBOARD.md)** - Dashboard UI guide and features
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Developer guide and API reference
- **[QUICKREF.md](QUICKREF.md)** - Quick reference card

## Common Commands

```bash
# Dashboard (web UI with charts)
python dashboard.py

# Command-line analysis
python main.py

# Run examples
python example.py

# Run tests
python -m pytest test_spytrade.py -v
```

## Use Cases

### Traders
- Monitor multiple assets simultaneously
- Get AI-powered trade recommendations
- Track technical indicators in real-time
- Analyze news sentiment impact

### Analysts
- Research market trends
- Backtest strategies
- Study price action patterns
- Analyze technical setups

### Developers
- Extend with custom indicators
- Integrate with trading APIs
- Build backtesting engines
- Create paper trading bots

## Disclaimer

⚠️ **IMPORTANT**: This application is for educational and research purposes only.

- Not financial advice
- No guarantees of profitability
- Past performance ≠ future results
- Always do your own research
- Never risk money you can't afford to lose
- Start with paper trading
- Use proper risk management

## Roadmap

- [ ] Backtesting engine
- [ ] Advanced ML models (neural networks)
- [ ] Options strategy analysis
- [ ] Multi-timeframe analysis
- [ ] WebSocket real-time data
- [ ] Telegram/Email alerts
- [ ] Paper trading simulation
- [ ] Integration with Interactive Brokers
- [ ] Drag-and-drop strategy builder
- [ ] Community signal sharing

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

Having issues? Check:
1. [SETUP.md](SETUP.md) - Installation help
2. [DASHBOARD.md](DASHBOARD.md) - UI troubleshooting
3. [spytrade.log](spytrade.log) - Error logs
4. [QUICKREF.md](QUICKREF.md) - Common solutions

## License

MIT License - See LICENSE file for details

---

**Last Updated**: November 16, 2025  
**Repository**: https://github.com/ajenkinsynwa/spyTrade  
**Questions?** Check the documentation or create an issue!
