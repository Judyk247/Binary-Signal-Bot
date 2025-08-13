import time
from datetime import datetime
from data_fetcher import get_market_data
from strategy import analyze_market
from telegram_utils import send_telegram_message
import os
from dotenv import load_dotenv

load_dotenv()

# Get list of 50 currency pairs
CURRENCY_PAIRS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "NZDUSD", "USDCAD",
    "EURGBP", "EURJPY", "GBPJPY", "CHFJPY", "AUDJPY", "NZDJPY", "CADJPY",
    "EURAUD", "GBPAUD", "AUDNZD", "AUDCAD", "AUDCHF", "CADCHF", "NZDCAD",
    "NZDCHF", "EURNZD", "GBPNZD", "USDHKD", "USDSEK", "USDSGD", "USDNOK",
    "USDZAR", "USDTRY", "EURCHF", "GBPCHF", "EURCAD", "GBPCAD", "EURSEK",
    "EURNOK", "EURTRY", "EURZAR", "AUDSGD", "NZDSGD", "SGDJPY", "CHFSGD",
    "CADSGD", "HKDJPY", "SEKJPY", "NOKJPY", "TRYJPY", "ZARJPY", "USDMXN"
]

# Timeframes and their strategy types
TIMEFRAMES = {
    "1m": "trend_following",
    "2m": "trend_following",
    "3m": "trend_following",
    "5m": "trend_reversal"
}

CHECK_INTERVAL = 10  # seconds

def main():
    print("🚀 Bot started... Monitoring market across timeframes.")

    while True:
        now = datetime.utcnow()
        seconds_to_next_candle = 60 - now.second
        
        # We want to run scan 30 seconds before candle open
        if seconds_to_next_candle == 30:
            for pair in CURRENCY_PAIRS:
                for tf, strategy_type in TIMEFRAMES.items():
                    try:
                        candles = get_market_data(pair, tf, limit=100)
                        if not candles:
                            continue

                        signal = analyze_market(candles, strategy_type)
                        if signal:
                            send_telegram_message(f"{pair} {tf} → {signal}")
                    
                    except Exception as e:
                        print(f"Error processing {pair} {tf}: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
