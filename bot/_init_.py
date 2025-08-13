# __init__.py
"""
Binary Options Strategy Package
Contains:
- strategy.py      → Trading logic for trend reversal (5m) and trend following (1m, 2m, 3m)
- data_fetcher.py  → Fetches OHLCV data for multiple timeframes & pairs
- telegram_utils.py → Telegram messaging functions
"""

from .strategy import scan_and_alert
from .data_fetcher import fetch_market_data
from .telegram_utils import send_telegram_message

__all__ = [
    "scan_and_alert",
    "fetch_market_data",
    "send_telegram_message"
]
