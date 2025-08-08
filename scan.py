import time
import threading
from strategy import analyze_signal
from utils import fetch_ohlc_data
from config import currency_pairs, timeframes

# This dictionary holds live signals per symbol and timeframe
active_signals = {}

def scan_market():
    while True:
        for symbol in currency_pairs:
            for tf in timeframes:
                try:
                    ohlc_data = fetch_ohlc_data(symbol, tf, 100)
                    signal = analyze_signal(symbol, ohlc_data)
                    if signal:
                        active_signals[(symbol, tf)] = signal
                    else:
                        active_signals.pop((symbol, tf), None)
                except Exception as e:
                    print(f"[ERROR] Scanning {symbol} {tf}: {str(e)}")
        time.sleep(30)  # Adjust as needed

def start_scanner():
    scanner_thread = threading.Thread(target=scan_market, daemon=True)
    scanner_thread.start()
