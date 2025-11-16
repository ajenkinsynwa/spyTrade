#!/usr/bin/env python3
"""
Example script showing how to use spyTrade components independently.
"""

from datetime import datetime
from config import config
from data.fetchers import DataFetcher, MarketDataProcessor
from analysis import TechnicalAnalyzer
from alerts import SignalGenerator
from news import SentimentAnalyzer

def example_fetch_data():
    """Example: Fetch market data."""
    print("=" * 60)
    print("EXAMPLE: Fetching Market Data")
    print("=" * 60)
    
    # Fetch SPY data
    print("\nFetching SPY data...")
    spy_candles = DataFetcher.fetch_stock_data_yfinance('SPY', period='100d', interval='30m')
    
    if spy_candles:
        print(f"Fetched {len(spy_candles)} SPY candles")
        last_candle = spy_candles[-1]
        print(f"Latest: {last_candle.timestamp} | Close: ${last_candle.close:.2f}")
    
    # Fetch Bitcoin data
    print("\nFetching Bitcoin data...")
    btc_candles = DataFetcher.fetch_crypto_data('BTC')
    
    if btc_candles:
        print(f"Fetched {len(btc_candles)} Bitcoin candles")
        last_candle = btc_candles[-1]
        print(f"Latest: {last_candle.timestamp} | Close: ${last_candle.close:.2f}")
    
    return spy_candles, btc_candles


def example_technical_analysis(candles):
    """Example: Technical analysis."""
    print("\n" + "=" * 60)
    print("EXAMPLE: Technical Analysis")
    print("=" * 60)
    
    if not candles:
        print("No data available")
        return
    
    # Calculate indicators
    indicators = TechnicalAnalyzer.calculate_all_indicators(candles)
    
    print(f"\nTechnical Indicators:")
    print(f"  RSI (14):        {indicators.rsi:.2f}" if indicators.rsi else "  RSI:             N/A")
    print(f"  MACD:            {indicators.macd:.4f}" if indicators.macd else "  MACD:            N/A")
    print(f"  SMA 20:          ${indicators.sma_20:.2f}" if indicators.sma_20 else "  SMA 20:          N/A")
    print(f"  SMA 50:          ${indicators.sma_50:.2f}" if indicators.sma_50 else "  SMA 50:          N/A")
    print(f"  BB Upper:        ${indicators.bollinger_upper:.2f}" if indicators.bollinger_upper else "  BB Upper:        N/A")
    print(f"  BB Lower:        ${indicators.bollinger_lower:.2f}" if indicators.bollinger_lower else "  BB Lower:        N/A")
    print(f"  ATR (14):        ${indicators.atr:.2f}" if indicators.atr else "  ATR:             N/A")
    
    # Identify support and resistance
    resistance, support = TechnicalAnalyzer.identify_resistance_support(candles)
    print(f"\nSupport & Resistance:")
    print(f"  Resistance:      ${resistance:.2f}")
    print(f"  Support:         ${support:.2f}")
    
    # Analyze price action
    price_action = TechnicalAnalyzer.analyze_price_action(candles)
    print(f"\nPrice Action:")
    print(f"  Trend:           {price_action.get('trend_type', 'N/A')}")
    print(f"  Bullish:         {price_action.get('is_bullish', False)}")
    print(f"  Patterns:        {', '.join(price_action.get('patterns', [])) or 'None'}")
    
    return indicators, price_action


def example_sentiment_analysis():
    """Example: News sentiment analysis."""
    print("\n" + "=" * 60)
    print("EXAMPLE: Sentiment Analysis")
    print("=" * 60)
    
    # Fetch news for SPY
    print("\nFetching news for SPY...")
    news_articles = DataFetcher.fetch_news('SPY', limit=5)
    
    if news_articles:
        print(f"Fetched {len(news_articles)} articles")
        
        # Analyze sentiment
        sentiment_summary = SentimentAnalyzer.get_sentiment_summary(news_articles)
        
        print(f"\nSentiment Summary:")
        print(f"  Average:         {sentiment_summary['average_sentiment']:.2f}")
        print(f"  Category:        {sentiment_summary['category']}")
        print(f"  Bullish:         {sentiment_summary['bullish_count']}")
        print(f"  Neutral:         {sentiment_summary['neutral_count']}")
        print(f"  Bearish:         {sentiment_summary['bearish_count']}")
    else:
        print("No news articles fetched")


def example_signal_generation(candles, indicators, price_action):
    """Example: Trade signal generation."""
    print("\n" + "=" * 60)
    print("EXAMPLE: Signal Generation")
    print("=" * 60)
    
    if not candles:
        print("No data available")
        return
    
    # Generate signal
    signal = SignalGenerator.generate_signal(
        symbol='SPY',
        candles=candles,
        technical_indicators=indicators,
        atr_value=indicators.atr
    )
    
    if signal:
        print(f"\nTrade Signal Generated:")
        print(f"  Signal Type:     {signal.signal_type}")
        print(f"  Confidence:      {signal.confidence:.1f}%")
        print(f"  Entry Price:     ${signal.entry_price:.2f}")
        print(f"  Stop Loss:       ${signal.stop_loss:.2f}")
        print(f"  Take Profit:     ${signal.take_profit:.2f}")
        
        risk_reward = (signal.take_profit - signal.entry_price) / (signal.entry_price - signal.stop_loss)
        print(f"  Risk/Reward:     {risk_reward:.2f} : 1")
        print(f"  Indicators:      {', '.join(signal.indicators_used)}")
    else:
        print("No signal generated (confidence below threshold)")


def main():
    """Run all examples."""
    print("\n" + "╔" + "=" * 58 + "╗")
    print("║" + " spyTrade - Component Examples".center(58) + "║")
    print("╚" + "=" * 58 + "╝\n")
    
    # Example 1: Fetch data
    spy_candles, btc_candles = example_fetch_data()
    
    # Example 2: Technical analysis
    if spy_candles:
        indicators, price_action = example_technical_analysis(spy_candles)
        
        # Example 3: Signal generation
        example_signal_generation(spy_candles, indicators, price_action)
    
    # Example 4: Sentiment analysis
    example_sentiment_analysis()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
