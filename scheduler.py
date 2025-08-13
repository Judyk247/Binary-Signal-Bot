# scheduler.py

import time
import threading
from datetime import datetime, timedelta
from data_fetcher import fetch_data
from strategy import check_trend_reversal, check_trend_following
from telegram_utils import send_telegram_message

# Currency pairs list (50)
CURRENCY_PAIRS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "USDCAD", "AUDUSD", "NZDUSD",
    "EURGBP", "EURJPY", "GBPJPY", "CHFJPY", "EURAUD", "GBPAUD", "AUDJPY",
    "AUDNZD", "AUDCAD", "AUDCHF", "CADJPY", "CADCHF", "EURNZD", "GBPNZD",
    "NZDJPY", "NZDCHF", "USDSEK", "USDNOK", "USDDKK", "USDZAR", "USDHKD",
    "USDSGD", "USDTRY", "EURCHF", "EURCAD", "EURSEK", "EURNOK", "EURDKK",
    "EURTRY", "GBPCHF", "GBPCAD", "GBPSEK", "GBPNOK", "GBPDKK", "GBPTRY",
    "AUDSGD", "AUDHKD", "AUDZAR", "CADSGD", "CHFSGD", "NZDSGD", "SGDJPY",
    "ZARJPY", "TRYJPY"
]

# Timeframes mapping for strategies
TIMEFRAMES = {
    "1m": "trend_following",
    "2m": "trend_following",
    "3m": "trend_following",
    "5m": "trend_reversal"
}

def run_strategy_for_timeframe(timeframe, strategy_type):
    """Run the appropriate strategy for each currency pair."""
    for symbol in CURRENCY_PAIRS:
        data = fetch_data(symbol, timeframe)
        if data is None:
            continue

        if strategy_type == "trend_reversal":
            signal = check_trend_reversal(symbol, data)
        else:
            signal = check_trend_following(symbol, data, timeframe)

        if signal:
            send_telegram_message(f"{timeframe} {strategy_type.upper()} signal: {symbol} → {signal}")

def schedule_task():
    """Run tasks 30 seconds before each candle opens."""
    while True:
        now = datetime.utcnow()
        seconds = now.second
        next_run = None

        # Find the closest timeframe alignment
        for tf in TIMEFRAMES.keys():
            minutes = int(tf.replace("m", ""))
            if now.minute % minutes == (minutes - 1) and seconds >= 30:
                next_run = tf
                break

        if next_run:
            strategy_type = TIMEFRAMES[next_run]
            print(f"[{datetime.utcnow()}] Running {strategy_type} for {next_run} timeframe...")
            run_strategy_for_timeframe(next_run, strategy_type)

            # Wait until the next possible execution
            time.sleep(60)
        else:
            time.sleep(1)

if __name__ == "__main__":
    scheduler_thread = threading.Thread(target=schedule_task)
    scheduler_thread.start()
