# data_fetcher.py

import requests
import pandas as pd
from datetime import datetime
from config import TWELVE_DATA_API_KEY

def fetch_heikin_ashi(symbol, interval="3min", outputsize=50):
    """
    Fetch Heikin Ashi candlesticks from Twelve Data API.
    Converts regular OHLC data to Heikin Ashi.
    """
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize={outputsize}&apikey={TWELVE_DATA_API_KEY}&format=JSON"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Twelve Data API request failed: {response.text}")

    data = response.json()
    if "values" not in data:
        raise Exception(f"Error in response: {data.get('message', 'Unknown error')}")

    df = pd.DataFrame(data["values"])
    df.rename(columns={"datetime": "time"}, inplace=True)
    df = df.sort_values("time").reset_index(drop=True)

    df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].astype(float)

    # Heikin Ashi calculation
    ha_df = pd.DataFrame()
    ha_df["time"] = df["time"]
    ha_df["close"] = ((df["open"] + df["high"] + df["low"] + df["close"]) / 4)

    ha_open = [(df["open"][0] + df["close"][0]) / 2]
    for i in range(1, len(df)):
        ha_open.append((ha_open[i - 1] + ha_df["close"][i - 1]) / 2)
    ha_df["open"] = ha_open

    ha_df["high"] = df[["high", "open", "close"]].max(axis=1)
    ha_df["low"] = df[["low", "open", "close"]].min(axis=1)

    ha_df = ha_df[["time", "open", "high", "low", "close"]]
    ha_df = ha_df[::-1].reset_index(drop=True)  # Reverse for most recent first

    return ha_df
