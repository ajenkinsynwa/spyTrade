"""News sentiment analysis."""
import logging
from typing import List, Optional, Dict
from textblob import TextBlob
import re

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Analyzes sentiment from news articles."""
    
    # Keyword-based sentiment dictionaries
    BULLISH_KEYWORDS = {
        'surge', 'surge ahead', 'rally', 'bullish', 'positive', 'gains',
        'outperform', 'upside', 'momentum', 'strength', 'breakout',
        'beat', 'profit', 'earnings', 'growth', 'upgrade', 'upgrade',
        'buy', 'overweight', 'positive', 'good news', 'strong', 'rebound'
    }
    
    BEARISH_KEYWORDS = {
        'crash', 'plunge', 'bearish', 'negative', 'losses', 'decline',
        'underperform', 'downside', 'weakness', 'breakdown', 'miss',
        'loss', 'miss', 'downgrade', 'sell', 'underweight', 'concern',
        'risk', 'warning', 'weak', 'slump', 'sell-off'
    }
    
    @staticmethod
    def analyze_article(article: Dict[str, str]) -> float:
        """
        Analyze sentiment of a single article.
        
        Args:
            article: Dictionary with 'headline' and optionally 'content'
            
        Returns:
            Sentiment score (-1.0 to 1.0)
        """
        text = article.get('headline', '') + ' ' + article.get('content', '')
        
        if not text.strip():
            return 0.0
        
        # Method 1: TextBlob sentiment analysis
        try:
            blob = TextBlob(text)
            textblob_sentiment = blob.sentiment.polarity  # -1 to 1
        except Exception as e:
            logger.warning(f"TextBlob analysis failed: {e}")
            textblob_sentiment = 0.0
        
        # Method 2: Keyword-based analysis
        text_lower = text.lower()
        keyword_sentiment = SentimentAnalyzer._keyword_sentiment(text_lower)
        
        # Combine both methods (weighted average)
        # TextBlob: 70%, Keywords: 30%
        combined_sentiment = (textblob_sentiment * 0.7) + (keyword_sentiment * 0.3)
        
        return float(combined_sentiment)
    
    @staticmethod
    def analyze_articles(articles: List[Dict[str, str]]) -> float:
        """
        Analyze sentiment of multiple articles.
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Average sentiment score (-1.0 to 1.0)
        """
        if not articles:
            return 0.0
        
        sentiments = [SentimentAnalyzer.analyze_article(article) for article in articles]
        
        return sum(sentiments) / len(sentiments)
    
    @staticmethod
    def _keyword_sentiment(text: str) -> float:
        """
        Calculate sentiment based on keyword frequency.
        
        Args:
            text: Text to analyze (should be lowercase)
            
        Returns:
            Sentiment score (-1.0 to 1.0)
        """
        # Count keyword occurrences
        bullish_count = sum(1 for keyword in SentimentAnalyzer.BULLISH_KEYWORDS 
                          if keyword in text)
        bearish_count = sum(1 for keyword in SentimentAnalyzer.BEARISH_KEYWORDS 
                           if keyword in text)
        
        total = bullish_count + bearish_count
        
        if total == 0:
            return 0.0
        
        # Neutral (50/50) = 0, Bullish majority = positive, Bearish majority = negative
        sentiment = (bullish_count - bearish_count) / total
        
        return float(sentiment)
    
    @staticmethod
    def categorize_sentiment(sentiment_score: float) -> str:
        """
        Categorize sentiment score into discrete categories.
        
        Args:
            sentiment_score: Score from -1 to 1
            
        Returns:
            Category string: 'Very Bullish', 'Bullish', 'Neutral', 'Bearish', 'Very Bearish'
        """
        if sentiment_score > 0.5:
            return 'Very Bullish'
        elif sentiment_score > 0.2:
            return 'Bullish'
        elif sentiment_score > -0.2:
            return 'Neutral'
        elif sentiment_score > -0.5:
            return 'Bearish'
        else:
            return 'Very Bearish'
    
    @staticmethod
    def get_sentiment_summary(articles: List[Dict[str, str]]) -> Dict:
        """
        Get comprehensive sentiment summary for articles.
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Dictionary with sentiment analysis
        """
        if not articles:
            return {
                'average_sentiment': 0.0,
                'category': 'Neutral',
                'bullish_count': 0,
                'bearish_count': 0,
                'neutral_count': 0,
                'total_articles': 0
            }
        
        sentiments = []
        bullish_count = 0
        bearish_count = 0
        neutral_count = 0
        
        for article in articles:
            sentiment = SentimentAnalyzer.analyze_article(article)
            sentiments.append(sentiment)
            
            if sentiment > 0.2:
                bullish_count += 1
            elif sentiment < -0.2:
                bearish_count += 1
            else:
                neutral_count += 1
        
        avg_sentiment = sum(sentiments) / len(sentiments)
        
        return {
            'average_sentiment': avg_sentiment,
            'category': SentimentAnalyzer.categorize_sentiment(avg_sentiment),
            'bullish_count': bullish_count,
            'bearish_count': bearish_count,
            'neutral_count': neutral_count,
            'total_articles': len(articles)
        }
