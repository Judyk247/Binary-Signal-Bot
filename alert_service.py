# alert_service.py

import time
from datetime import datetime, timedelta
from telegram_utils import send_telegram_message
from strategy import check_signals  # strategy.py should handle both 1m/2m/3m trend-following & 5m trend-reversal
from data_fetcher import fetch_latest_candles  # data_fetcher.py should handle multi-timeframe fetching

# Timeframes to scan: 1m, 2m, 3m, 5m
TIMEFRAMES = ["1m", "2m", "3m", "5m"]

# Currency pairs list (same as strategy.py)
CURRENCY_PAIRS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD",
    "EURGBP", "EURJPY", "GBPJPY", "AUDJPY", "CADJPY", "CHFJPY", "EURAUD",
    "EURNZD", "GBPAUD", "GBPCAD", "GBPNZD", "AUDCAD", "AUDCHF", "AUDNZD",
    "CADCHF", "NZDCAD", "NZDCHF", "XAUUSD", "XAGUSD", "BTCUSD", "ETHUSD",
    "LTCUSD", "XRPUSD", "EURCAD", "EURCHF", "NZDJPY", "USDHKD", "USDNOK",
    "USDSEK", "USDSGD", "USDTRY", "USDZAR", "EURSEK", "EURTRY", "EURZAR",
    "GBPNOK", "GBPSGD", "GBPSEK", "GBPNZD", "AUDSGD", "AUDSEK", "NZDSGD", "CHFSGD"
]

ALERT_BEFORE_SECONDS = 30


def seconds_to_next_candle(timeframe: str) -> int:
    """Returns seconds remaining until the next candle open for a given timeframe."""
    now = datetime.utcnow()
    tf_minutes = int(timeframe.replace("m", ""))
    next_candle = (now.replace(second=0, microsecond=0) +
                   timedelta(minutes=tf_minutes))
    return int((next_candle - now).total_seconds())


def run_alert_loop():
    print("✅ Alert service started...")
    while True:
        for tf in TIMEFRAMES:
            seconds_left = seconds_to_next_candle(tf)
            if seconds_left == ALERT_BEFORE_SECONDS:
                print(f"[{tf}] ⏳ {ALERT_BEFORE_SECONDS}s before new candle — checking signals...")
                for pair in CURRENCY_PAIRS:
                    try:
                        candles = fetch_latest_candles(pair, tf, 60)  # Fetch last 60 candles
                        signal = check_signals(pair, tf, candles)
                        if signal:
                            message = f"{tf} | {pair} | {signal['type']} | {signal['details']}"
                            send_telegram_message(message)
                    except Exception as e:
                        print(f"❌ Error fetching {pair} on {tf}: {e}")
        time.sleep(1)


if __name__ == "__main__":
    run_alert_loop()
