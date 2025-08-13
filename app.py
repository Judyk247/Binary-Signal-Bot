# app.py
import os
import time
import signal
import sys
from dotenv import load_dotenv

from data_fetcher import DataFetcher
from strategy import Strategy

# Load .env variables
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("Missing TELEGRAM_TOKEN or TELEGRAM_CHAT_ID in .env file")

# Currency pairs
CURRENCY_PAIRS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "USDCAD", "AUDUSD", "NZDUSD",
    "EURGBP", "EURJPY", "GBPJPY", "AUDJPY", "CADJPY", "CHFJPY", "EURAUD",
    "GBPAUD", "AUDCAD", "AUDCHF", "AUDNZD", "CADCHF", "EURNZD", "GBPCAD",
    "GBPCHF", "GBPNZD", "NZDCAD", "NZDCHF", "NZDJPY", "USDNOK", "USDSEK",
    "USDSGD", "USDHKD", "USDZAR", "EURCAD", "EURCHF", "EURDKK", "EURHUF",
    "EURPLN", "EURSEK", "EURTRY", "EURZAR", "GBPDKK", "GBPNOK", "GBPSEK",
    "GBPTRY", "CHFPLN", "CHFSEK", "JPYSEK", "NOKSEK", "TRYJPY", "ZARJPY"
]

# Timeframes: 1m, 2m, 3m (trend following) & 5m (trend reversal)
TIMEFRAMES = ["1m", "2m", "3m", "5m"]

# Create DataFetcher and Strategy instances
fetcher = DataFetcher(pairs=CURRENCY_PAIRS, timeframes=TIMEFRAMES)
strategy = Strategy(telegram_token=TELEGRAM_TOKEN, telegram_chat_id=TELEGRAM_CHAT_ID)

# Graceful shutdown flag
running = True


def handle_exit(sig, frame):
    global running
    print("\nStopping application...")
    running = False


signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)


def main_loop():
    global running
    print("📊 Binary Options Bot Started.")
    print("Monitoring pairs:", ", ".join(CURRENCY_PAIRS))
    print("Using timeframes:", ", ".join(TIMEFRAMES))
    print("Press Ctrl+C to stop.")

    while running:
        try:
            for tf in TIMEFRAMES:
                for pair in CURRENCY_PAIRS:
                    candles = fetcher.get_candles(pair, tf)

                    if candles is None or len(candles) < 50:
                        continue  # Not enough data to process

                    if tf == "5m":
                        # Apply trend reversal strategy
                        signal_info = strategy.check_trend_reversal(candles, pair, tf)
                    else:
                        # Apply trend following strategy
                        signal_info = strategy.check_trend_following(candles, pair, tf)

                    if signal_info:
                        strategy.send_alert(signal_info)

            time.sleep(1)  # Check every second for near-candle-open alerts

        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main_loop()
