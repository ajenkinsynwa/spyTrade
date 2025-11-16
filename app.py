"""Flask web server for spyTrade dashboard."""
import json
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import plotly
import plotly.graph_objs as go
from threading import Thread
import time

from config import config
from data.fetchers import DataFetcher, MarketDataProcessor
from analysis import TechnicalAnalyzer
from alerts import SignalGenerator
from news import SentimentAnalyzer

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Store latest data for dashboard
dashboard_data = {
    'SPY': {
        'candles': [],
        'indicators': {},
        'signal': None,
        'news_sentiment': None,
        'last_updated': None
    },
    'BTC-USD': {
        'candles': [],
        'indicators': {},
        'signal': None,
        'news_sentiment': None,
        'last_updated': None
    }
}

# Background update thread
update_thread = None
is_running = False


@app.route('/')
def index():
    """Serve the main dashboard page."""
    return render_template('index.html')


@app.route('/api/symbols')
def get_symbols():
    """Get list of available symbols."""
    return jsonify({
        'symbols': config.SYMBOLS,
        'current_symbol': 'SPY'
    })


@app.route('/api/chart-data/<symbol>')
def get_chart_data(symbol):
    """Get chart data with technical indicators for a symbol."""
    if symbol not in dashboard_data:
        return jsonify({'error': 'Symbol not found'}), 404
    
    data = dashboard_data[symbol]
    
    if not data['candles']:
        return jsonify({'error': 'No data available'}), 404
    
    # Prepare chart data
    chart_data = {
        'symbol': symbol,
        'candles': [
            {
                'timestamp': c.timestamp.isoformat(),
                'open': c.open,
                'high': c.high,
                'low': c.low,
                'close': c.close,
                'volume': c.volume
            }
            for c in data['candles']
        ],
        'indicators': data['indicators'],
        'last_updated': data['last_updated'].isoformat() if data['last_updated'] else None
    }
    
    return jsonify(chart_data)


@app.route('/api/signal/<symbol>')
def get_signal(symbol):
    """Get latest trade signal for a symbol."""
    if symbol not in dashboard_data:
        return jsonify({'error': 'Symbol not found'}), 404
    
    signal = dashboard_data[symbol]['signal']
    
    if signal:
        return jsonify(signal.to_dict())
    else:
        return jsonify({'signal_type': 'HOLD', 'confidence': 0})


@app.route('/api/sentiment/<symbol>')
def get_sentiment(symbol):
    """Get sentiment analysis for a symbol."""
    if symbol not in dashboard_data:
        return jsonify({'error': 'Symbol not found'}), 404
    
    sentiment = dashboard_data[symbol]['news_sentiment']
    
    if sentiment:
        return jsonify(sentiment)
    else:
        return jsonify({
            'average_sentiment': 0.0,
            'category': 'Neutral',
            'bullish_count': 0,
            'bearish_count': 0,
            'neutral_count': 0,
            'total_articles': 0
        })


@app.route('/api/stats/<symbol>')
def get_stats(symbol):
    """Get market statistics for a symbol."""
    if symbol not in dashboard_data:
        return jsonify({'error': 'Symbol not found'}), 404
    
    data = dashboard_data[symbol]
    
    if not data['candles']:
        return jsonify({'error': 'No data available'}), 404
    
    candles = data['candles']
    price_processor = MarketDataProcessor()
    
    # Calculate statistics
    current_price = candles[-1].close
    price_change = price_processor.calculate_price_change(candles)
    volume_sma = price_processor.calculate_volume_sma(candles)
    
    # Calculate high/low for period
    prices = [c.close for c in candles]
    high_price = max(c.high for c in candles)
    low_price = min(c.low for c in candles)
    
    return jsonify({
        'current_price': current_price,
        'price_change_percent': price_change,
        'high': high_price,
        'low': low_price,
        'volume_sma': volume_sma,
        'total_candles': len(candles)
    })


def update_dashboard_data():
    """Update dashboard data in the background."""
    global is_running
    
    while is_running:
        try:
            for symbol in config.SYMBOLS:
                logger.info(f"Updating data for {symbol}")
                
                # Fetch data
                if symbol == 'BTC-USD' or symbol == 'BTC':
                    candles = DataFetcher.fetch_crypto_data('BTC')
                else:
                    candles = DataFetcher.fetch_stock_data_yfinance(symbol)
                
                if candles:
                    # Calculate indicators
                    indicators = TechnicalAnalyzer.calculate_all_indicators(candles)
                    
                    # Fetch news and sentiment
                    news = DataFetcher.fetch_news(symbol)
                    sentiment = SentimentAnalyzer.get_sentiment_summary(news)
                    
                    # Generate signal
                    signal = SignalGenerator.generate_signal(
                        symbol=symbol,
                        candles=candles,
                        technical_indicators=indicators,
                        news_sentiment=sentiment.get('average_sentiment', 0.0),
                        atr_value=indicators.atr
                    )
                    
                    # Update dashboard data
                    dashboard_data[symbol] = {
                        'candles': candles,
                        'indicators': indicators.to_dict(),
                        'signal': signal,
                        'news_sentiment': sentiment,
                        'last_updated': datetime.now()
                    }
                    
                    logger.info(f"Updated {symbol} - Signal: {signal.signal_type if signal else 'None'}")
        
        except Exception as e:
            logger.error(f"Error updating dashboard data: {e}", exc_info=True)
        
        # Wait for next update interval
        time.sleep(config.UPDATE_INTERVAL)


@app.route('/api/start-updates')
def start_updates():
    """Start background data updates."""
    global update_thread, is_running
    
    if not is_running:
        is_running = True
        update_thread = Thread(target=update_dashboard_data, daemon=True)
        update_thread.start()
        
        return jsonify({'status': 'Updates started'})
    
    return jsonify({'status': 'Updates already running'})


@app.route('/api/stop-updates')
def stop_updates():
    """Stop background data updates."""
    global is_running
    
    is_running = False
    
    return jsonify({'status': 'Updates stopped'})


@app.route('/api/manual-update/<symbol>')
def manual_update(symbol):
    """Manually trigger an update for a symbol."""
    if symbol not in dashboard_data:
        return jsonify({'error': 'Symbol not found'}), 404
    
    try:
        # Fetch data
        if symbol == 'BTC-USD' or symbol == 'BTC':
            candles = DataFetcher.fetch_crypto_data('BTC')
        else:
            candles = DataFetcher.fetch_stock_data_yfinance(symbol)
        
        if candles:
            # Calculate indicators
            indicators = TechnicalAnalyzer.calculate_all_indicators(candles)
            
            # Fetch news and sentiment
            news = DataFetcher.fetch_news(symbol)
            sentiment = SentimentAnalyzer.get_sentiment_summary(news)
            
            # Generate signal
            signal = SignalGenerator.generate_signal(
                symbol=symbol,
                candles=candles,
                technical_indicators=indicators,
                news_sentiment=sentiment.get('average_sentiment', 0.0),
                atr_value=indicators.atr
            )
            
            # Update dashboard data
            dashboard_data[symbol] = {
                'candles': candles,
                'indicators': indicators.to_dict(),
                'signal': signal,
                'news_sentiment': sentiment,
                'last_updated': datetime.now()
            }
            
            return jsonify({
                'status': 'success',
                'symbol': symbol,
                'signal': signal.signal_type if signal else 'HOLD',
                'last_updated': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'Failed to fetch data'}), 500
    
    except Exception as e:
        logger.error(f"Error in manual update: {e}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


def create_app():
    """Create and configure the Flask app."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
