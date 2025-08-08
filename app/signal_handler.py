# signal_handler.py

import time
from indicators import analyze_chart
from postbot import send_signal_to_telegram
from config import SYMBOLS, TIMEFRAMES, SIGNAL_INTERVAL, STRATEGY_NAME

last_sent = {}

def handle_signals():
    while True:
        current_time = int(time.time())
        for symbol in SYMBOLS:
            for tf in TIMEFRAMES:
                key = f"{symbol}_{tf}"
                last_signal_time = last_sent.get(key, 0)

                # Only check again if enough time has passed
                if current_time - last_signal_time >= SIGNAL_INTERVAL:
                    signal = analyze_chart(symbol, tf)
                    if signal:
                        message = f"🔔 *{STRATEGY_NAME} Signal*\n\n" \
                                  f"Symbol: `{symbol}`\n" \
                                  f"Timeframe: `{tf}`\n" \
                                  f"Direction: *{signal}*\n" \
                                  f"Time: `{time.strftime('%Y-%m-%d %H:%M:%S')}`"
                        send_signal_to_telegram(message)
                        last_sent[key] = current_time
        time.sleep(5)
