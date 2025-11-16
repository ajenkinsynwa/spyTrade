# spyTrade Dashboard UI Guide

## Overview

The spyTrade Dashboard is a modern, responsive web-based interface for real-time trading analysis. It provides TradingView-style charting with live technical indicators, trade signals, and sentiment analysis.

## Features

### 📊 Real-Time Charts
- **Interactive Candlestick Charts**: Full OHLCV data visualization
- **Technical Overlay**: SMA 20 and SMA 50 moving averages
- **Volume Analysis**: Volume bars color-coded by candle direction
- **Responsive Design**: Works on desktop, tablet, and mobile

### 🎯 Trade Signals
- **Signal Type**: BUY, SELL, or HOLD recommendations
- **Confidence Level**: 0-100% confidence score with visual progress bar
- **Price Levels**:
  - Entry Price: Current market price
  - Stop Loss: Risk management level
  - Take Profit: Target profit level
- **Risk/Reward Ratio**: Automatically calculated for position sizing

### 📈 Technical Indicators
Real-time display of:
- **RSI (14)**: Momentum oscillator (overbought/oversold)
- **MACD**: Trend and momentum (line, signal, histogram)
- **SMA 20**: Short-term trend
- **SMA 50**: Medium-term trend
- **ATR**: Volatility measure

### 📰 News Sentiment
- **Overall Sentiment**: Bullish, Bearish, or Neutral classification
- **Article Counts**: Breakdown of sentiment distribution
- **Real-time Updates**: Latest news for selected symbol

### 💱 Multi-Symbol Support
- SPY (S&P 500)
- BTC-USD (Bitcoin)
- Easily extensible for more symbols

## Dashboard Layout

```
┌─────────────────────────────────────────────────────┐
│  Header: Symbol Selector | Refresh | Live Toggle   │
├─────────────────────────────────────────────────────┤
│              Stats Bar (Price, Change, High, Low)   │
├─────────────────────────────────────────────────────┤
│                                                       │
│              Interactive Price Chart                │
│              (Candlestick + Moving Averages)        │
│                                                       │
├───────────────────────┬───────────────────────────┤
│                       │                             │
│  Signal Analysis      │  Technical Indicators      │
│  - Signal Type        │  - RSI, MACD, SMA, ATR    │
│  - Confidence         │  - Live Values            │
│  - Entry/SL/TP        │                           │
│  - Risk/Reward        │                           │
│                       ├───────────────────────────┤
│                       │  News Sentiment           │
│                       │  - Bullish/Bearish/Neut. │
│                       │  - Article Counts         │
│                       │  - Total Articles         │
└───────────────────────┴───────────────────────────┘
└─────────────────────────────────────────────────────┘
```

## Color Scheme

| Element | Color | Meaning |
|---------|-------|---------|
| Background | Dark Gray | Primary UI background |
| Accent | Blue | Primary action color |
| Success/Buy | Green | Bullish signals |
| Danger/Sell | Red | Bearish signals |
| Warning/Hold | Amber | Neutral conditions |
| Text | Light Gray | Primary text |
| Border | Medium Gray | Element borders |

## Controls

### Header Controls

#### Symbol Selector
```
Dropdown menu to select analysis symbol:
- SPY: S&P 500 ETF
- BTC-USD: Bitcoin
```

#### Refresh Button (🔄)
Manually triggers an immediate update of all dashboard data.

#### Live Toggle (▶/⏸)
- **▶ Start Live**: Enables automatic 30-minute updates
- **⏸ Stop Live**: Disables automatic updates
- **Status Indicator**: Green dot = live, Red dot = offline

### Chart Interactions

- **Zoom**: Scroll to zoom in/out
- **Pan**: Click and drag to pan
- **Hover**: Shows OHLCV values and indicators
- **Range Slider**: (Bottom) Quick zoom to different periods

## API Endpoints

### Data Endpoints

#### GET `/api/chart-data/<symbol>`
Returns OHLCV candle data and indicator values.

```json
{
  "symbol": "SPY",
  "candles": [
    {
      "timestamp": "2025-11-16T10:00:00",
      "open": 450.0,
      "high": 451.5,
      "low": 449.5,
      "close": 450.5,
      "volume": 1000000
    }
  ],
  "indicators": {
    "rsi": 55.2,
    "macd": 0.245,
    "sma_20": 449.8,
    "sma_50": 448.2
  }
}
```

#### GET `/api/stats/<symbol>`
Returns market statistics for a symbol.

```json
{
  "current_price": 450.50,
  "price_change_percent": 2.35,
  "high": 451.80,
  "low": 449.20,
  "volume_sma": 1250000,
  "total_candles": 100
}
```

#### GET `/api/signal/<symbol>`
Returns the latest trade signal.

```json
{
  "symbol": "SPY",
  "signal_type": "BUY",
  "confidence": 72.5,
  "entry_price": 450.50,
  "stop_loss": 441.80,
  "take_profit": 467.75,
  "reasoning": "...",
  "indicators_used": ["RSI", "MACD", "MA"],
  "timestamp": "2025-11-16T10:30:00"
}
```

#### GET `/api/sentiment/<symbol>`
Returns sentiment analysis from news.

```json
{
  "average_sentiment": 0.35,
  "category": "Bullish",
  "bullish_count": 5,
  "bearish_count": 1,
  "neutral_count": 2,
  "total_articles": 8
}
```

### Control Endpoints

#### GET `/api/manual-update/<symbol>`
Manually triggers an update for a symbol.

```json
{
  "status": "success",
  "symbol": "SPY",
  "signal": "BUY",
  "last_updated": "2025-11-16T10:30:00"
}
```

#### GET `/api/start-updates`
Starts automatic background updates.

#### GET `/api/stop-updates`
Stops automatic background updates.

## Usage Guide

### Basic Workflow

1. **Open Dashboard**
   ```bash
   python dashboard.py
   ```
   Browser will automatically open to http://localhost:5000

2. **Select Symbol**
   Use dropdown to select SPY or BTC-USD

3. **View Chart**
   - Observe price action and moving averages
   - Identify trends and key levels
   - Hover for detailed OHLCV values

4. **Read Signal**
   - Check signal type (BUY/SELL/HOLD)
   - Review confidence percentage
   - Note entry, stop loss, take profit levels

5. **Enable Live Mode**
   Click "Start Live" button to enable 30-minute automatic updates

6. **Monitor Sentiment**
   Check news sentiment for additional context

### Interpreting Signals

**BUY Signal (Green)**
- Confidence > 60%
- Multiple bullish indicators aligned
- Consider entering long positions
- Use provided stop loss for risk management

**SELL Signal (Red)**
- Confidence < 40%
- Multiple bearish indicators aligned
- Consider exiting long or entering short
- Protect profits with take profit level

**HOLD Signal (Amber)**
- Confidence 40-60%
- Mixed or unclear signals
- Wait for clearer direction
- Monitor for signal change

### Chart Analysis

**Candlestick Colors**
- **Green**: Close > Open (bullish)
- **Red**: Close < Open (bearish)

**Volume Bars**
- **Green**: Volume on up candles
- **Red**: Volume on down candles
- Larger = higher trading activity

**Moving Averages**
- **Blue Line**: SMA 20 (short-term trend)
- Crosses SMA 50 for trend changes

### Risk Management

**Stop Loss**
- Maximum acceptable loss level
- Automatically calculated using ATR
- Place stop below this level

**Take Profit**
- Target profit level
- Automatically calculated using ATR
- Place take profit above this level

**Risk/Reward Ratio**
- (Take Profit - Entry) / (Entry - Stop Loss)
- Higher ratio = better risk-adjusted trade
- Typical target: 2:1 or better

## Customization

### Adding More Symbols

Edit `config/__init__.py`:
```python
SYMBOLS = ['SPY', 'BTC-USD', 'QQQ', 'NVDA']
```

The symbol will automatically appear in the dropdown.

### Changing Chart Colors

Edit CSS in `templates/index.html`:
```css
:root {
    --success: #10b981;  /* Buy signal color */
    --danger: #ef4444;   /* Sell signal color */
    --accent: #3b82f6;   /* Primary UI color */
}
```

### Adjusting Update Interval

Edit `config/__init__.py`:
```python
UPDATE_INTERVAL = 1800  # 30 minutes in seconds
```

⚠️ Must respect API rate limits!

## Performance Tips

1. **Reduce Candles**: Fewer historical candles = faster loading
2. **Disable Live Mode**: Manual refresh uses fewer API calls
3. **Limit Symbols**: Fewer symbols = faster updates
4. **Clear Browser Cache**: Removes old data

## Troubleshooting

### Chart Not Loading
```
1. Check browser console (F12)
2. Verify API keys in .env
3. Check internet connection
4. Try manual refresh (🔄 button)
```

### Live Updates Not Working
```
1. Check status indicator color
2. Verify API rate limits not exceeded
3. Check spytrade.log for errors
4. Try stopping and restarting live mode
```

### Signals Not Appearing
```
1. Verify confidence threshold met (>60% for BUY)
2. Check symbol has data (manual refresh)
3. Review technical indicators (all present?)
4. Check spytrade.log for signal generation details
```

### Page Loads Slowly
```
1. Close unnecessary browser tabs
2. Clear browser cache
3. Reduce number of symbols
4. Decrease chart candle count
```

## Browser Support

- ✅ Chrome/Chromium 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ⚠️ Mobile browsers (limited full functionality)

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `F12` | Open Developer Tools |
| `Ctrl+R` | Refresh Page |
| `Ctrl+L` | Focus Address Bar |

## Mobile Access

Dashboard is responsive and works on mobile devices:

1. Get your computer's IP address:
   ```bash
   ipconfig getifaddr en0  # macOS/Linux
   ```

2. Access from mobile:
   ```
   http://<YOUR_IP>:5000
   ```

3. Responsive layout automatically adjusts for screen size

## Security Notes

⚠️ **Running Locally**
- Dashboard is designed for local use
- Do not expose to internet without authentication
- No sensitive data is stored in browser

**Production Deployment**
- Add HTTPS/SSL certificate
- Implement authentication
- Use environment variables for API keys
- Run behind reverse proxy (nginx)
- Add rate limiting

## Advanced Features

### Export Data
Right-click chart → Save image as PNG

### Extend Dashboard
Modify `templates/index.html` to add:
- Additional indicators
- Custom alerts
- Integration with trading APIs
- Backtesting results

---

**Last Updated**: November 16, 2025
**Questions?** Check SETUP.md or DEVELOPMENT.md
