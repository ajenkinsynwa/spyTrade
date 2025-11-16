"""
SPYTRADE - Real-Time Trade Advice Application
Visual Architecture & Data Flow Diagrams
"""

"""
═══════════════════════════════════════════════════════════════════════════════
                         DATA FLOW DIAGRAM
═══════════════════════════════════════════════════════════════════════════════

                            ┌─────────────────┐
                            │  Free APIs      │
                            ├─────────────────┤
                            │ • yfinance      │
                            │ • CoinGecko     │
                            │ • Finnhub       │
                            │ • NewsAPI       │
                            └────────┬────────┘
                                     │
                                     ▼
                    ┌────────────────────────────────┐
                    │  DATA FETCHER                  │
                    │ (data/fetchers.py)             │
                    │ • fetch_stock_data()           │
                    │ • fetch_crypto_data()          │
                    │ • fetch_news()                 │
                    └────────────┬───────────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
       ┌──────────────────┐          ┌───────────────────┐
       │ Candle Objects   │          │  News Articles    │
       │ (OHLCV data)     │          │  (Text)           │
       └────────┬─────────┘          └─────────┬─────────┘
                │                              │
                │          ┌──────────────────┘
                │          ▼
                │   ┌──────────────────────┐
                │   │ SENTIMENT ANALYZER   │
                │   │ (news/__init__.py)   │
                │   │ • TextBlob NLP       │
                │   │ • Keyword matching   │
                │   └──────────┬───────────┘
                │              │
                │    ┌─────────▼──────────┐
                │    │ Sentiment Score    │
                │    │ (-1.0 to 1.0)      │
                │    └─────────┬──────────┘
                │              │
                ▼              │
       ┌───────────────────┐   │
       │ TECHNICAL         │   │
       │ ANALYZER          │   │
       │ (analysis/)       │   │
       ├───────────────────┤   │
       │ • RSI (14)        │   │
       │ • MACD            │   │
       │ • SMA 20/50       │   │
       │ • Bollinger Bands │   │
       │ • ATR             │   │
       │ • Price Action    │   │
       │ • Resistance/Sup. │   │
       └─────────┬─────────┘   │
                 │             │
                 │  ┌──────────┘
                 ▼  ▼
       ┌──────────────────────────┐
       │ SIGNAL GENERATOR         │
       │ (alerts/__init__.py)     │
       │                          │
       │ Score Components:        │
       │ • RSI Score (20%)        │
       │ • MACD Score (20%)       │
       │ • Price Action (20%)     │
       │ • Moving Avg (15%)       │
       │ • Bollinger Bands (10%)  │
       │ • News Sentiment (10%)   │
       │ • ML Prediction (5%)     │
       └─────────┬────────────────┘
                 │
                 ▼
       ┌──────────────────────────┐
       │ TRADE SIGNAL             │
       ├──────────────────────────┤
       │ • Signal Type (BUY/SELL) │
       │ • Confidence Score       │
       │ • Entry Price            │
       │ • Stop Loss              │
       │ • Take Profit            │
       │ • Risk/Reward Ratio      │
       │ • Reasoning              │
       └─────────┬────────────────┘
                 │
        ┌────────┴──────────┐
        ▼                   ▼
    ┌────────────┐   ┌──────────────┐
    │  Console   │   │  JSON File   │
    │  Output    │   │  (Historical)│
    └────────────┘   └──────────────┘

═══════════════════════════════════════════════════════════════════════════════
                      CONFIDENCE SCORING SYSTEM
═══════════════════════════════════════════════════════════════════════════════

                    Each Indicator Scores 0-100

    ┌──────────────────────────────────────────────────────────┐
    │ RSI (Relative Strength Index)          Weight: 20%       │
    │ ├─ RSI < 30 (Oversold):   75 points   │
    │ ├─ RSI 30-40:              60 points   │
    │ ├─ RSI 40-60 (Neutral):    50 points   │
    │ ├─ RSI 60-70:              40 points   │
    │ └─ RSI > 70 (Overbought):  25 points   │
    └──────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────┐
    │ MACD (Moving Avg Conv. Div.)         Weight: 20%         │
    │ ├─ Histogram > 0, MACD > Signal:  65 points │
    │ └─ Histogram < 0, MACD < Signal:  35 points │
    └──────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────┐
    │ Price Action Patterns                 Weight: 20%         │
    │ ├─ Strong bullish candle:      +15 points │
    │ ├─ Hammer pattern:              +10 points │
    │ ├─ Uptrend:                     +10 points │
    │ ├─ Strong bearish candle:      -15 points │
    │ └─ Shooting star:              -10 points │
    └──────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────┐
    │ Moving Averages                       Weight: 15%         │
    │ ├─ SMA20 > SMA50:              60 points │
    │ ├─ SMA20 < SMA50:              40 points │
    │ └─ Price > Both MAs:           +10 points │
    └──────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────┐
    │ Bollinger Bands                       Weight: 10%         │
    │ ├─ Near upper band (>80%):     35 points │
    │ ├─ Middle (40-60%):            50 points │
    │ └─ Near lower band (<20%):     65 points │
    └──────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────┐
    │ News Sentiment Analysis               Weight: 10%         │
    │ ├─ Very Bullish (>0.5):        75 points │
    │ ├─ Bullish (0.2-0.5):          60 points │
    │ ├─ Neutral (-0.2-0.2):         50 points │
    │ ├─ Bearish (-0.5 to -0.2):     40 points │
    │ └─ Very Bearish (<-0.5):       25 points │
    └──────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────┐
    │ ML Prediction                         Weight: 5%          │
    │ ├─ Bullish prediction:         65 points │
    │ ├─ Neutral prediction:         50 points │
    │ └─ Bearish prediction:         35 points │
    └──────────────────────────────────────────────────────────┘

                              ↓ ↓ ↓

                    WEIGHTED AVERAGE CALCULATION

        Confidence = (
            RSI×0.20 + MACD×0.20 + PA×0.20 + MA×0.15 +
            BB×0.10 + Sentiment×0.10 + ML×0.05
        )

                              ↓ ↓ ↓

                        SIGNAL DETERMINATION

        IF Confidence > 60%  → BUY  (Bullish Setup)
        IF Confidence < 40%  → SELL (Bearish Setup)
        IF 40-60%           → HOLD (Uncertain)

═══════════════════════════════════════════════════════════════════════════════
                       RISK MANAGEMENT CALCULATIONS
═══════════════════════════════════════════════════════════════════════════════

For a BUY signal at Entry Price = $450.00, ATR = $5.00:

    Stop Loss = Entry - (ATR × 1.5)
             = $450.00 - ($5.00 × 1.5)
             = $450.00 - $7.50
             = $442.50

    Take Profit = Entry + (ATR × 2.0)
               = $450.00 + ($5.00 × 2.0)
               = $450.00 + $10.00
               = $460.00

    Risk = Entry - Stop Loss = $450.00 - $442.50 = $7.50
    Reward = Take Profit - Entry = $460.00 - $450.00 = $10.00

    Risk/Reward Ratio = Reward / Risk = $10.00 / $7.50 = 1.33 : 1
    (For every $1 risked, you could make $1.33)

═══════════════════════════════════════════════════════════════════════════════
                        TECHNICAL INDICATORS REFERENCE
═══════════════════════════════════════════════════════════════════════════════

RSI (Relative Strength Index) - Momentum Oscillator
┌─────────────────────────────────────────┐
│ Range: 0-100                            │
│ Period: 14 (default)                    │
│                                         │
│  100  ┌─────┐                           │
│       │Overbought (>70)                │
│  70   ├─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┐    │
│       │                           │    │
│  50   │     Neutral Zone          │    │
│       │                           │    │
│  30   ├─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┤    │
│       │Oversold (<30)             │    │
│   0   └─────────────────────────┘    │
│                                         │
│ High RSI = Momentum ↑ (possibly top)   │
│ Low RSI = Momentum ↓ (possibly bottom) │
└─────────────────────────────────────────┘

MACD (Moving Average Convergence Divergence) - Trend & Momentum
┌──────────────────────────────────────┐
│ 3 Lines:                             │
│  1. MACD line (12-EMA - 26-EMA)     │
│  2. Signal line (9-EMA of MACD)     │
│  3. Histogram (MACD - Signal)       │
│                                      │
│ Bullish: MACD > Signal & Hist > 0   │
│ Bearish: MACD < Signal & Hist < 0   │
│ Strength: Width of histogram        │
└──────────────────────────────────────┘

Moving Averages - Trend Direction
┌──────────────────────────────────────┐
│ SMA 20 (Short-term trend)            │
│ SMA 50 (Long-term trend)             │
│                                      │
│ Price ↑ SMA20 ↑ SMA50 = Uptrend   │
│ Price ↓ SMA20 ↓ SMA50 = Downtrend │
│                                      │
│ Golden Cross: SMA20 > SMA50 (Bullish)│
│ Death Cross: SMA20 < SMA50 (Bearish) │
└──────────────────────────────────────┘

Bollinger Bands - Volatility & Price Levels
┌──────────────────────────────────────┐
│  ┌─────────────────── Upper Band    │
│  │                                   │
│  │   ╱╲  Price in bands = Normal    │
│  │  ╱  ╲                            │
│  │ ╱    ╲ ── Middle Band (SMA)      │
│  │        ╲                         │
│  │─────────╲──── Lower Band        │
│  │                                   │
│ Band Width = Volatility             │
│ Price near top = Overbought         │
│ Price near bot = Oversold           │
└──────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
                           FILE STRUCTURE
═══════════════════════════════════════════════════════════════════════════════

spyTrade/
│
├── README.md                 ← Project overview
├── SETUP.md                  ← Installation & usage guide
├── QUICKREF.md              ← Quick reference commands
├── DEVELOPMENT.md           ← Developer guide
│
├── requirements.txt         ← Python package dependencies
├── .env.example             ← Environment variable template
├── .gitignore              ← Git ignore patterns
│
├── config/
│   └── __init__.py          ← Centralized configuration & API keys
│
├── data/
│   ├── __init__.py          ← Data models (Candle, Signal, Indicators)
│   └── fetchers.py          ← API data fetching & processing
│
├── analysis/
│   ├── __init__.py          ← Technical indicator calculations
│   └── ai_models.py         ← ML utilities & pattern detection
│
├── alerts/
│   └── __init__.py          ← Trade signal generation & scoring
│
├── news/
│   └── __init__.py          ← Sentiment analysis & NLP
│
├── main.py                  ← Main application entry point
├── example.py              ← Usage examples for each component
├── test_spytrade.py        ← Unit tests
│
├── signals_history.json     ← Generated trade signals (created at runtime)
└── spytrade.log            ← Application logs (created at runtime)

═══════════════════════════════════════════════════════════════════════════════
                         EXECUTION FLOW (MAIN.PY)
═══════════════════════════════════════════════════════════════════════════════

START
  │
  ▼
┌─────────────────────────────┐
│ Initialize SpyTradeApp      │
│ Load configuration          │
│ Set up logging              │
└──────────┬──────────────────┘
           │
           ▼
      ┌────────────────────────────────────┐
      │ For Each Configured Symbol:        │
      │ (SPY, BTC-USD, QQQ, etc)          │
      └───────────┬──────────────────────┘
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
    ┌────────────┐   ┌──────────────┐
    │ Fetch Stock│   │ Fetch Crypto │
    │ Data       │   │ Data         │
    │(yfinance)  │   │(CoinGecko)   │
    └────────┬───┘   └────────┬─────┘
             │                │
             └────────┬───────┘
                      ▼
            ┌──────────────────────┐
            │ Calculate Indicators │
            │ • RSI, MACD, SMA, BB │
            │ • Price Action       │
            │ • Resistance/Support │
            └─────────┬────────────┘
                      │
                      ▼
            ┌──────────────────────┐
            │ Fetch News           │
            │ (Finnhub/NewsAPI)    │
            └────────┬─────────────┘
                     │
                     ▼
            ┌──────────────────────┐
            │ Analyze Sentiment    │
            │ (TextBlob + Keywords)│
            └────────┬─────────────┘
                     │
                     ▼
            ┌──────────────────────┐
            │ Generate Signal      │
            │ Calculate Confidence │
            │ Determine Entry/SL/TP│
            └────────┬─────────────┘
                     │
              ┌──────┴──────┐
              ▼             ▼
        ┌─────────────┐ ┌──────────────┐
        │ Print to    │ │ Save to      │
        │ Console     │ │ signals_     │
        │ & Log       │ │ history.json │
        └─────────────┘ └──────────────┘
                      │
            ┌─────────┘
            │
            ▼
    ┌──────────────────────────┐
    │ Sleep for UPDATE_INTERVAL│
    │ (Default: 1800 sec / 30m)│
    └────────────┬─────────────┘
                 │
                 ├─ Go back to "For Each Symbol" loop
                 │
                 └─ Repeat forever (or once if once=True)

END

═══════════════════════════════════════════════════════════════════════════════
"""

print(__doc__)
