"""Data models for market data."""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional

@dataclass
class Candle:
    """Represents a candlestick/bar of market data."""
    timestamp: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    
    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)

@dataclass
class TechnicalIndicators:
    """Container for technical indicator values."""
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_middle: Optional[float] = None
    bollinger_lower: Optional[float] = None
    atr: Optional[float] = None
    
    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)

@dataclass
class MarketData:
    """Complete market data for analysis."""
    symbol: str
    candles: list  # List of Candle objects
    indicators: TechnicalIndicators
    volume_sma: Optional[float] = None
    price_change_percent: Optional[float] = None
    last_updated: Optional[datetime] = None

@dataclass
class TradeSignal:
    """Represents a trade signal."""
    symbol: str
    signal_type: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float  # 0-100
    entry_price: float
    stop_loss: float
    take_profit: float
    reasoning: str
    indicators_used: list  # List of indicators that contributed to signal
    timestamp: datetime
    
    def to_dict(self):
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = data['timestamp'].isoformat()
        return data
