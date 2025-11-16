# spyTrade - Real-Time Trade Advice Application

A real-time trading advice application that analyzes S&P 500 (SPY) and Bitcoin on 30-minute timeframes using AI, technical analysis, and free market data APIs.

## Features

- **Real-time Data Collection**
  - Price data from free APIs (Alpha Vantage, Finnhub, CoinGecko)
  - Live trade volume analysis
  - Market news integration

- **Technical Analysis**
  - Resistance and support area identification
  - Price action pattern recognition
  - Technical indicators (RSI, MACD, Moving Averages)
  - Volume analysis

- **AI-Powered Insights**
  - Machine learning models for pattern recognition
  - Historical data analysis for trend prediction
  - Sentiment analysis from news feeds

- **Real-time Alerts**
  - Trade signal generation
  - Entry/exit recommendations
  - Risk management suggestions

## Project Structure

```
spyTrade/
├── config/
│   ├── __init__.py
│   └── api_keys.py          # API configuration (not committed)
├── data/
│   ├── __init__.py
│   ├── fetchers.py          # Data fetching from APIs
│   └── data_models.py       # Data structures
├── analysis/
│   ├── __init__.py
│   ├── technical.py         # Technical analysis calculations
│   ├── patterns.py          # Price action patterns
│   └── ai_models.py         # AI/ML models
├── alerts/
│   ├── __init__.py
│   └── signal_generator.py  # Trade signal generation
├── news/
│   ├── __init__.py
│   └── sentiment.py         # News sentiment analysis
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── .env.example             # Example environment variables
└── README.md
```

## Free APIs Used

1. **Alpha Vantage** - Stock price data and technical indicators
2. **CoinGecko** - Bitcoin data (no API key required)
3. **Finnhub** - Stock news and sentiment
4. **NewsAPI** - General market news
5. **CCXT** - Cryptocurrency data

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ajenkinsynwa/spyTrade.git
cd spyTrade
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up API keys:
```bash
cp .env.example .env
# Add your free API keys to .env
```

5. Run the application:
```bash
python main.py
```

## Getting Free API Keys

- **Alpha Vantage**: https://www.alphavantage.co/ (free tier available)
- **Finnhub**: https://finnhub.io/ (free tier available)
- **NewsAPI**: https://newsapi.org/ (free tier available)
- **CoinGecko**: No API key required

## Trade Signals

The application generates three types of signals:
- **BUY**: Strong bullish indicators
- **SELL**: Strong bearish indicators
- **HOLD**: Neutral or uncertain conditions

Each signal includes:
- Confidence score (0-100%)
- Supporting technical indicators
- Risk/reward ratio
- Historical backtest performance

## License

MIT
