# data_fetcher.py

import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")

# List of 50 currency pairs
CURRENCY_PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "USD/CHF", "NZD/USD", "EUR/GBP", "EUR/JPY", "GBP/JPY",
    "AUD/JPY", "CAD/JPY", "CHF/JPY", "NZD/JPY", "EUR/AUD", "GBP/AUD", "AUD/NZD", "AUD/CAD", "AUD/CHF", "CAD/CHF",
    "EUR/CAD", "EUR/CHF", "GBP/CAD", "GBP/CHF", "NZD/CAD", "NZD/CHF", "EUR/NZD", "GBP/NZD", "USD/CNH", "USD/SGD",
    "USD/HKD", "USD/TRY", "USD/ZAR", "EUR/TRY", "GBP/TRY", "AUD/SGD", "NZD/SGD", "CAD/SGD", "CHF/SGD", "EUR/SGD",
    "GBP/SGD", "AUD/HKD", "NZD/HKD", "CAD/HKD", "CHF/HKD", "EUR/HKD", "GBP/HKD", "AUD/TRY", "NZD/TRY", "CAD/TRY"
]

# Map timeframes to Twelve Data format
TIMEFRAME_MAP = {
    "1m": "1min",
    "2m": "2min",
    "3m": "3min",
    "5m": "5min"
}

def fetch_data(symbol, timeframe, output_size=100):
    """
    Fetch OHLCV data for a given symbol and timeframe.
    """
    if timeframe not in TIMEFRAME_MAP:
        raise ValueError(f"Invalid timeframe: {timeframe}")

    url = f"https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": TIMEFRAME_MAP[timeframe],
        "apikey": TWELVE_DATA_API_KEY,
        "outputsize": output_size
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if "values" not in data:
            print(f"Error fetching data for {symbol} ({timeframe}): {data}")
            return None

        df = pd.DataFrame(data["values"])
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.astype({
            "open": float,
            "high": float,
            "low": float,
            "close": float,
            "volume": float
        })
        df = df.sort_values(by="datetime").reset_index(drop=True)
        return df

    except Exception as e:
        print(f"Error fetching data for {symbol} ({timeframe}): {e}")
        return None

def fetch_all_pairs(timeframes=["1m", "2m", "3m", "5m"]):
    """
    Fetch data for all currency pairs and given timeframes.
    Returns a dict: {(symbol, timeframe): DataFrame}
    """
    market_data = {}
    for pair in CURRENCY_PAIRS:
        for tf in timeframes:
            df = fetch_data(pair, tf)
            if df is not None:
                market_data[(pair, tf)] = df
    return market_data

if __name__ == "__main__":
    # Example: Fetch all data for testing
    data = fetch_all_pairs()
    print(f"Fetched data for {len(data)} pair-timeframe combinations.")
