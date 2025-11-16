# How to Start spyTrade - Complete Guide

## Quick Start (30 seconds)

### macOS/Linux
```bash
cd /Users/alexjenkins/Desktop/spyTrade
chmod +x start.sh
./start.sh
```

### Windows
```cmd
cd C:\Users\YourUsername\Desktop\spyTrade
start.bat
```

The dashboard will automatically open in your browser at **http://localhost:5000**

---

## Manual Setup (If Preferred)

### Step 1: Navigate to Project Directory
```bash
cd /Users/alexjenkins/Desktop/spyTrade
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
```

### Step 3: Activate Virtual Environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Configure API Keys (Optional)
```bash
cp .env.example .env
# Edit .env and add your API keys (optional - defaults work)
```

### Step 6: Run Dashboard
```bash
python dashboard.py
```

Browser will automatically open to **http://localhost:5000**

---

## Running Different Ways

### Option 1: Web Dashboard (Recommended)
```bash
python dashboard.py
```
- Opens interactive web interface
- Real-time charts with Plotly
- Professional TradingView-style UI
- Works on desktop, tablet, mobile

### Option 2: Command Line Analysis
```bash
python main.py
```
- Runs analysis once
- Outputs to console and logs
- Good for scripting/automation
- Can be looped with a scheduler

### Option 3: View Examples
```bash
python example.py
```
- Shows how to use individual components
- Demonstrates data fetching
- Shows technical analysis
- Helpful for learning the codebase

### Option 4: Run Tests
```bash
python -m pytest test_spytrade.py -v
```
- Runs unit tests
- Verifies installation is correct
- Checks data models work

---

## What Happens When You Start

When you run `python dashboard.py` or `./start.sh`:

1. **Server Starts**
   ```
   Running on http://127.0.0.1:5000
   ```

2. **Browser Opens**
   - Automatically opens to http://localhost:5000
   - If not, open manually in your browser

3. **Dashboard Loads**
   - Shows SPY (S&P 500) by default
   - Shows current price and stats
   - Displays technical indicators

4. **Click "Refresh" or "Start Live"**
   - Refresh: One-time data update
   - Start Live: Auto-update every 30 minutes

5. **View Results**
   - Interactive chart with candlesticks
   - Technical indicators (RSI, MACD, SMA)
   - Trade signal (BUY/SELL/HOLD)
   - News sentiment

---

## Dashboard Controls

### 📊 Symbol Selector
Top-left dropdown to choose:
- **SPY**: S&P 500 (default)
- **BTC-USD**: Bitcoin

### 🔄 Refresh Button
Manually fetch latest data immediately (one-time)

### ▶/⏸ Live Toggle
- **▶ Start Live**: Enable automatic 30-min updates
- **⏸ Stop Live**: Disable auto-updates
- Green dot = Live, Red dot = Offline

### 📈 Interactive Chart
- **Scroll**: Zoom in/out
- **Drag**: Pan left/right
- **Hover**: See price details
- **Double-click**: Reset zoom

---

## First-Time Setup Checklist

- [ ] Navigate to `/Users/alexjenkins/Desktop/spyTrade`
- [ ] Run `./start.sh` (macOS/Linux) or `start.bat` (Windows)
- [ ] Wait for "Dashboard will open..." message
- [ ] Browser opens to http://localhost:5000
- [ ] See SPY chart with indicators
- [ ] Click "Refresh" to fetch latest data
- [ ] See BUY/SELL/HOLD signal
- [ ] Click "Start Live" for auto-updates
- [ ] Select "BTC-USD" and refresh
- [ ] See Bitcoin analysis

---

## Troubleshooting Startup

### "Python is not installed"
**Solution**: Install Python 3.8+ from https://www.python.org/

### "Permission denied" (macOS/Linux)
```bash
chmod +x start.sh
./start.sh
```

### "Module not found" errors
```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Port 5000 already in use
```bash
# Option 1: Kill process using port 5000
lsof -i :5000  # Find PID
kill -9 <PID>

# Option 2: Use different port
# Edit app.py, change: app.run(..., port=5001)
```

### Browser doesn't auto-open
```
1. Manually go to http://localhost:5000
2. Or check terminal for URL and copy/paste
```

### No data appears in dashboard
```
1. Click "Refresh" button manually
2. Check internet connection
3. Wait a few seconds for API to respond
4. Check .env has correct API keys (or empty for defaults)
5. See spytrade.log for error messages
```

### API rate limit errors
```
1. Wait 60+ seconds (API free tier limits)
2. Increase UPDATE_INTERVAL in config/__init__.py
3. Use fewer symbols in SYMBOLS list
4. Don't click refresh too frequently
```

---

## Environment Variables (.env)

Optional configuration file (create from `.env.example`):

```bash
# API Keys (all optional - defaults work)
ALPHA_VANTAGE_API_KEY=demo
FINNHUB_API_KEY=your_key_here
NEWS_API_KEY=your_key_here

# Settings
UPDATE_INTERVAL=1800          # 30 minutes
SYMBOLS=SPY,BTC-USD           # Comma-separated
LOOKBACK_PERIOD=100           # Number of candles
```

**Note**: Application works without API keys using free/public APIs!

---

## Getting API Keys (Optional)

If you want more frequent updates or additional features:

### Alpha Vantage (Stock Data)
1. Visit: https://www.alphavantage.co/
2. Click "GET FREE API KEY"
3. Enter email
4. Copy key from email
5. Add to `.env`: `ALPHA_VANTAGE_API_KEY=your_key`

### Finnhub (Stock News - Recommended)
1. Visit: https://finnhub.io/
2. Sign up for free account
3. Copy API key from dashboard
4. Add to `.env`: `FINNHUB_API_KEY=your_key`

### NewsAPI (General News)
1. Visit: https://newsapi.org/
2. Sign up for free
3. Copy API key
4. Add to `.env`: `NEWS_API_KEY=your_key`

### CoinGecko (Crypto)
- ✅ NO KEY REQUIRED!
- Completely free, unlimited
- Used automatically for Bitcoin

---

## Common Startup Patterns

### Daily Automated Analysis (Cron - macOS/Linux)
```bash
# Edit crontab
crontab -e

# Add this line to run at 9:30 AM daily
30 9 * * * /Users/alexjenkins/Desktop/spyTrade/venv/bin/python /Users/alexjenkins/Desktop/spyTrade/main.py >> /Users/alexjenkins/Desktop/spyTrade/cron.log 2>&1
```

### Task Scheduler (Windows)
1. Open "Task Scheduler"
2. Create new task
3. Set trigger (daily at 9:30 AM)
4. Set action: `python main.py` in spyTrade directory
5. Set to run whether user logged in or not

### Background Service (systemd - Linux)
See SETUP.md for systemd service configuration

---

## System Requirements

### Minimum
- Python 3.8+
- 500MB disk space
- 100MB RAM
- Internet connection

### Recommended
- Python 3.10+
- 1GB disk space
- 500MB RAM
- Stable internet (broadband)

### Browsers
- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

---

## Performance Tips

1. **Faster startup**: App caches dependencies after first run
2. **Better performance**: Keep browser dev tools closed
3. **Reduce API calls**: Only use "Refresh" when needed
4. **Monitor resources**: Open terminal to see memory usage

---

## Keeping It Running

### Development/Testing
Just run `./start.sh` whenever you want to use it

### Continuous Monitoring
```bash
# Run in background (macOS/Linux)
nohup python dashboard.py > dashboard.log 2>&1 &

# Or use screen/tmux
screen -S spytrade
python dashboard.py
# Ctrl+A then D to detach
# screen -r spytrade to reattach
```

### Server Deployment
See DEVELOPMENT.md for production deployment options

---

## Next Steps After Starting

1. ✅ Dashboard loads at http://localhost:5000
2. 📊 View SPY chart and analysis
3. 💱 Switch to BTC-USD and analyze
4. 🎯 Read the trade signal (BUY/SELL/HOLD)
5. 📈 Click "Start Live" for auto-updates
6. 📰 Check news sentiment
7. 🔍 Explore technical indicators
8. 💡 Review DASHBOARD.md for advanced features
9. 🛠️ Customize settings in config/__init__.py if desired
10. 📚 Read SETUP.md and DEVELOPMENT.md for more info

---

## Getting Help

| Issue | Resource |
|-------|----------|
| Installation problems | SETUP.md |
| Dashboard features | DASHBOARD.md |
| Customization | DEVELOPMENT.md |
| Quick reference | QUICKREF.md |
| Errors in console | Check spytrade.log |
| API issues | See API docs (links in SETUP.md) |
| Code questions | See PROJECT_SUMMARY.md |

---

## Common Commands Reference

```bash
# Activate virtual environment
source venv/bin/activate

# Start dashboard (recommended)
python dashboard.py

# Run once
python main.py

# See examples
python example.py

# Run tests
python -m pytest test_spytrade.py -v

# Check Python version
python --version

# List installed packages
pip list

# Update package
pip install --upgrade package_name

# Deactivate virtual environment
deactivate

# Check if port is in use
lsof -i :5000

# View logs
tail -f spytrade.log
```

---

**Ready to start?** Run `./start.sh` and enjoy your trading analysis dashboard! 🚀

Questions? Check the documentation or see QUICKREF.md for quick answers.
