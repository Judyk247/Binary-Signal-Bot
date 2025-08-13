# signal_handler.py

import logging
from datetime import datetime
from strategy import check_trend_reversal_5m, check_trend_following
from telegram_utils import send_telegram_message

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Timeframe to strategy mapping
TIMEFRAME_STRATEGIES = {
    "1m": lambda df, pair: check_trend_following(df, pair, timeframe="1m"),
    "2m": lambda df, pair: check_trend_following(df, pair, timeframe="2m"),
    "3m": lambda df, pair: check_trend_following(df, pair, timeframe="3m"),
    "5m": lambda df, pair: check_trend_reversal_5m(df, pair)
}


def process_candles(timeframe, pair, df):
    """
    Main signal processing entry point.
    :param timeframe: str - e.g. "1m", "2m", "3m", "5m"
    :param pair: str - currency pair like "EURUSD"
    :param df: DataFrame - OHLCV data
    """
    if timeframe not in TIMEFRAME_STRATEGIES:
        logging.warning(f"Timeframe {timeframe} not supported.")
        return

    strategy_func = TIMEFRAME_STRATEGIES[timeframe]

    try:
        signal = strategy_func(df, pair)

        if signal:
            direction, reason = signal.get("direction"), signal.get("reason")
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

            message = (
                f"📊 {timeframe.upper()} Signal\n"
                f"Pair: {pair}\n"
                f"Direction: {direction}\n"
                f"Reason: {reason}\n"
                f"Time: {timestamp}"
            )

            send_telegram_message(message)
            logging.info(f"Signal sent for {pair} ({timeframe}): {direction}")
        else:
            logging.debug(f"No signal for {pair} ({timeframe})")

    except Exception as e:
        logging.error(f"Error processing {pair} ({timeframe}): {e}", exc_info=True)
