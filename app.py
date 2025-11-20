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
from analysis.ai_models import MLPredictor
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


@app.route('/favicon.ico')
def favicon():
    """Return a simple favicon."""
    return '', 204


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
    indicators = dashboard_data[symbol].get('indicators', {})
    
    if signal:
        signal_dict = signal.to_dict()
    else:
        signal_dict = {'signal_type': 'HOLD', 'confidence': 0}
    
    # Add technical indicators to response
    signal_dict['technical_indicators'] = {
        'rsi': indicators.get('rsi'),
        'macd': indicators.get('macd'),
        'macd_signal': indicators.get('macd_signal'),
        'sma_20': indicators.get('sma_20'),
        'sma_50': indicators.get('sma_50'),
        'atr': indicators.get('atr'),
        'bollinger_upper': indicators.get('bollinger_upper'),
        'bollinger_lower': indicators.get('bollinger_lower'),
    }
    
    return jsonify(signal_dict)


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


@app.route('/api/ai-prediction/<symbol>')
def get_ai_prediction(symbol):
    """Get AI/ML price prediction for a symbol."""
    if symbol not in dashboard_data:
        return jsonify({'error': 'Symbol not found'}), 404
    
    data = dashboard_data[symbol]
    
    if not data['candles']:
        return jsonify({'error': 'No data available'}), 404
    
    try:
        candles = data['candles']
        prices = [c.close for c in candles]
        
        # Get AI prediction
        prediction, confidence = MLPredictor.predict_next_move(prices)
        
        # Detect support/resistance levels
        resistances, supports = MLPredictor.detect_support_resistance_clusters(prices)
        
        # Calculate volatility regime
        volatility_regime = MLPredictor.calculate_volatility_regime(prices)
        
        # Identify patterns
        patterns = MLPredictor.identify_patterns(candles)
        
        return jsonify({
            'prediction': float(prediction) if prediction is not None else 0,
            'confidence': float(confidence),
            'direction': 'BULLISH' if (prediction or 0) > 0.1 else 'BEARISH' if (prediction or 0) < -0.1 else 'NEUTRAL',
            'resistance_levels': [float(r) for r in resistances[:3]],  # Top 3
            'support_levels': [float(s) for s in supports[:3]],  # Top 3
            'volatility_regime': volatility_regime,
            'patterns': patterns,
            'current_price': float(candles[-1].close),
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in AI prediction: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai-summary/<symbol>')
def get_ai_summary(symbol):
    """Get a comprehensive AI analysis summary."""
    if symbol not in dashboard_data:
        return jsonify({'error': 'Symbol not found'}), 404
    
    data = dashboard_data[symbol]
    
    if not data['candles']:
        return jsonify({'error': 'No data available'}), 404
    
    try:
        candles = data['candles']
        prices = [c.close for c in candles]
        indicators = data['indicators']
        
        # Get all AI metrics
        prediction, confidence = MLPredictor.predict_next_move(prices)
        resistances, supports = MLPredictor.detect_support_resistance_clusters(prices)
        volatility_regime = MLPredictor.calculate_volatility_regime(prices)
        patterns = MLPredictor.identify_patterns(candles)
        
        # Combine with technical indicators
        current_price = candles[-1].close
        rsi = indicators.get('rsi', 50)
        macd = indicators.get('macd', 0)
        sma_short = indicators.get('sma_short', current_price)
        sma_long = indicators.get('sma_long', current_price)
        
        # Generate trading recommendation
        buy_signals = 0
        
        # Check RSI
        if rsi < 30:
            buy_signals += 1
        elif rsi > 70:
            buy_signals -= 1
        
        # Check MACD
        if macd > 0:
            buy_signals += 1
        else:
            buy_signals -= 1
        
        # Check Price vs SMAs
        if current_price > sma_short > sma_long:
            buy_signals += 1
        elif current_price < sma_short < sma_long:
            buy_signals -= 1
        
        # Check AI prediction
        if prediction and prediction > 0.1:
            buy_signals += 1
        elif prediction and prediction < -0.1:
            buy_signals -= 1
        
        recommendation = 'STRONG BUY' if buy_signals >= 3 else 'BUY' if buy_signals == 2 else 'HOLD' if buy_signals == 1 else 'SELL' if buy_signals == -2 else 'STRONG SELL' if buy_signals <= -3 else 'NEUTRAL'
        
        return jsonify({
            'symbol': symbol,
            'recommendation': recommendation,
            'confidence_score': float(confidence) * 100 if confidence else 0,
            'current_price': float(current_price),
            'ai_prediction': {
                'direction': 'BULLISH' if (prediction or 0) > 0.1 else 'BEARISH' if (prediction or 0) < -0.1 else 'NEUTRAL',
                'strength': float(abs(prediction or 0))
            },
            'technical_analysis': {
                'rsi': float(rsi),
                'macd': float(macd),
                'sma_short': float(sma_short),
                'sma_long': float(sma_long)
            },
            'resistance_levels': [float(r) for r in resistances[:3]],
            'support_levels': [float(s) for s in supports[:3]],
            'volatility': volatility_regime,
            'patterns': patterns,
            'signals_count': buy_signals,
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in AI summary: {e}")
        return jsonify({'error': str(e)}), 500


def update_dashboard_data():
    """Update dashboard data in the background."""
    global is_running
    
    while is_running:
        try:
            for symbol in config.SYMBOLS:
                logger.info(f"Updating data for {symbol}")
                
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
                        
                        logger.info(f"Updated {symbol} - Signal: {signal.signal_type if signal else 'None'}")
                    else:
                        logger.warning(f"No data available for {symbol}")
                
                except Exception as e:
                    logger.error(f"Error updating {symbol}: {e}", exc_info=True)
                    continue
        
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
            try:
                news = DataFetcher.fetch_news(symbol)
                sentiment = SentimentAnalyzer.get_sentiment_summary(news)
            except Exception as e:
                logger.warning(f"Could not fetch news for {symbol}: {e}")
                sentiment = {
                    'average_sentiment': 0.0,
                    'category': 'Neutral',
                    'bullish_count': 0,
                    'bearish_count': 0,
                    'neutral_count': 0,
                    'total_articles': 0
                }
            
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
            return jsonify({'error': 'Failed to fetch data for ' + symbol}), 500
    
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
    
    # Start background updates automatically
    import sys
    sys.modules[__name__].is_running = True
    sys.modules[__name__].update_thread = Thread(target=update_dashboard_data, daemon=True)
    sys.modules[__name__].update_thread.start()
    logger.info("Background data updates started")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
