# scan.py

import time
import pandas as pd
from datetime import datetime, timedelta
from data_fetcher import fetch_ohlcv
from strategy import check_trend_reversal_5m, check_trend_following
from telegram_utils import send_telegram_message

# List of 50 currency pairs
SYMBOLS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD", "EURGBP",
    "EURJPY", "GBPJPY", "AUDJPY", "CADJPY", "CHFJPY", "EURAUD", "GBPAUD", "AUDCAD",
    "AUDCHF", "AUDNZD", "CADCHF", "EURNZD", "GBPCAD", "GBPCHF", "GBPNZD", "NZDCAD",
    "NZDCHF", "USDNOK", "USDSEK", "USDSGD", "USDHKD", "USDZAR", "USDMXN", "EURSEK",
    "EURCHF", "EURCAD", "EURSGD", "EURZAR", "GBPSEK", "GBPNOK", "AUDSGD", "NZDSGD",
    "CHFSGD", "CADSGD", "SGDJPY", "ZARJPY", "NOKJPY", "SEKJPY", "HKDJPY", "MXNJPY",
    "XAUUSD", "XAGUSD"
]

# Mapping timeframes to strategies
TIMEFRAMES = {
    "1m": "trend_following",
    "2m": "trend_following",
    "3m": "trend_following",
    "5m": "trend_reversal"
}

def scan_and_alert():
    while True:
        now = datetime.utcnow()

        for tf, strategy_type in TIMEFRAMES.items():
            # Calculate seconds until next candle
            if tf.endswith("m"):
                minutes = int(tf.replace("m", ""))
                next_candle_time = now.replace(second=0, microsecond=0) + timedelta(minutes=minutes)
                seconds_until_next = (next_candle_time - now).total_seconds()

                # Only run checks 30 seconds before new candle
                if 25 <= seconds_until_next <= 35:
                    for symbol in SYMBOLS:
                        try:
                            df = fetch_ohlcv(symbol, tf, limit=100)

                            if strategy_type == "trend_reversal":
                                signal = check_trend_reversal_5m(df)
                            else:
                                signal = check_trend_following(df, tf)

                            if signal:
                                message = f"[{tf}] {symbol} → {signal.upper()} Signal detected."
                                send_telegram_message(message)

                        except Exception as e:
                            print(f"Error scanning {symbol} ({tf}): {e}")

        time.sleep(1)  # Keep CPU usage low

if __name__ == "__main__":
    scan_and_alert()
