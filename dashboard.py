"""
Desktop application launcher for spyTrade dashboard.
Uses Flask to serve the web UI and automatically opens it in the default browser.
"""
import webbrowser
import os
import time
from threading import Thread
from app import create_app, is_running

def open_browser(url, delay=2):
    """Open browser after delay to allow server to start."""
    time.sleep(delay)
    webbrowser.open(url)

def main():
    """Start the Flask server and open dashboard in browser."""
    app = create_app()
    
    # Open browser in background thread
    url = 'http://localhost:5000'
    browser_thread = Thread(target=open_browser, args=(url,), daemon=True)
    browser_thread.start()
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                 spyTrade Dashboard Starting                  ║
    ╚══════════════════════════════════════════════════════════════╝
    
    📊 Opening dashboard in your default browser...
    🌐 Server running at: http://localhost:5000
    
    Features:
    ✓ Real-time price charts with technical indicators
    ✓ Live trade signals with confidence levels
    ✓ Risk/Reward analysis
    ✓ News sentiment tracking
    ✓ Multiple symbol support
    
    Press Ctrl+C to stop the server
    """)
    
    # Start Flask app
    app.run(debug=False, host='0.0.0.0', port=5001)

if __name__ == '__main__':
    main()
