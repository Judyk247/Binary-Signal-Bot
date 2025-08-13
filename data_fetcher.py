# data_fetcher.py
import os
import time
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from strategy import check_trade_signal
from telegram_utils import send_telegram_message
import ccxt  # You can replace with broker-specific API wrapper

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Timeframes to monitor
TIMEFRAMES = {
    "1m": "trend_following",
    "2m": "trend_following",
    "3m": "trend_following",
    "5m": "trend_reversal"
}

# 50 currency pairs
CURRENCY_PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "USD/CHF",
    "NZD/USD", "EUR/GBP", "EUR/JPY", "GBP/JPY", "AUD/JPY", "CAD/JPY",
    "CHF/JPY", "NZD/JPY", "EUR/AUD", "EUR/CAD", "EUR/CHF", "EUR/NZD",
    "GBP/AUD", "GBP/CAD", "GBP/CHF", "GBP/NZD", "AUD/CAD", "AUD/CHF",
    "AUD/NZD", "CAD/CHF", "NZD/CAD", "NZD/CHF", "USD/SGD", "EUR/SGD",
    "GBP/SGD", "AUD/SGD", "NZD/SGD", "USD/HKD", "USD/SEK", "USD/NOK",
    "USD/DKK", "USD/ZAR", "USD/TRY", "USD/MXN", "EUR/SEK", "EUR/NOK",
    "EUR/DKK", "EUR/TRY", "EUR/ZAR", "GBP/SEK", "GBP/NOK", "GBP/TRY",
    "GBP/ZAR", "AUD/TRY"
]

# Initialize exchange (demo with CCXT)
exchange = ccxt.binance({
    "apiKey": API_KEY,
    "secret": API_SECRET
})

def fetch_ohlc(pair, timeframe, limit=100):
    """Fetch OHLCV data for a given pair and timeframe."""
    try:
        symbol = pair.replace("/", "")
        ohlc = exchange.fetch_ohlcv(pair, timeframe, limit=limit)
        df = pd.DataFrame(ohlc, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df
    except Exception as e:
        print(f"[ERROR] Failed to fetch data for {pair} ({timeframe}): {e}")
        return None

def scan_and_alert():
    """Check all pairs and timeframes, send alert 30s before candle close."""
    while True:
        now = datetime.utcnow()
        seconds_to_next_candle = 60 - (now.second % 60)

        # Only scan 30 seconds before the candle closes
        if seconds_to_next_candle == 30:
            for pair in CURRENCY_PAIRS:
                for tf, strategy_type in TIMEFRAMES.items():
                    df = fetch_ohlc(pair, tf, limit=100)
                    if df is None or len(df) < 50:
                        continue

                    # Check trade signal from strategy.py
                    signal = check_trade_signal(df, strategy_type)

                    if signal:
                        msg = f"📊 {pair} | {tf} | {strategy_type.upper()} | {signal}"
                        send_telegram_message(TELEGRAM_CHAT_ID, msg)
                        print(f"[ALERT] {msg}")

        time.sleep(1)  # Keep loop responsive

if __name__ == "__main__":
    print("[INFO] Starting Data Fetcher...")
    scan_and_alert()
