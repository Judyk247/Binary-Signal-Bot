# signal.py

import requests
import datetime
from utils import *
import pandas as pd
import numpy as np

API_KEY = 'c1516b63b0e54828bc83861b9676501f'
BASE_URL = 'https://api.twelvedata.com/time_series'

def fetch_data(symbol, interval, length=100):
    params = {
        'symbol': symbol,
        'interval': interval,
        'outputsize': length,
        'apikey': API_KEY,
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if 'values' not in data:
        return None

    df = pd.DataFrame(data['values'])
    df = df.rename(columns={
        'datetime': 'time',
        'open': 'open',
        'high': 'high',
        'low': 'low',
        'close': 'close'
    })
    df = df.astype({'open': 'float', 'high': 'float', 'low': 'float', 'close': 'float'})
    df = df.sort_values('time')

    return df.reset_index(drop=True)


def calculate_indicators(df):
    # EMA-150
    df['ema150'] = df['close'].ewm(span=150, adjust=False).mean()

    # Stochastic (14,3,3)
    low_min = df['low'].rolling(window=14).min()
    high_max = df['high'].rolling(window=14).max()
    df['%K'] = 100 * ((df['close'] - low_min) / (high_max - low_min))
    df['%D'] = df['%K'].rolling(window=3).mean()

    # Alligator (13,8,5)
    df['jaw'] = df['close'].rolling(window=13).mean().shift(8)
    df['teeth'] = df['close'].rolling(window=8).mean().shift(5)
    df['lips'] = df['close'].rolling(window=5).mean().shift(3)

    # Heikin Ashi candles
    ha_df = df.copy()
    ha_df['ha_close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    ha_df['ha_open'] = (df['open'] + df['close']) / 2
    df['ha_close'] = ha_df['ha_close']
    df['ha_open'] = ha_df['ha_open']

    return df


def check_buy_condition(row):
    # Strategy conditions for Buy
    return (
        row['ha_close'] > row['ema150']
        and row['ha_close'] > row['jaw'] > row['teeth'] > row['lips']
        and row['%K'] > 30
        and row['%K'] > row['%D']
    )


def check_sell_condition(row):
    # Strategy conditions for Sell
    return (
        row['ha_close'] < row['ema150']
        and row['ha_close'] < row['jaw'] < row['teeth'] < row['lips']
        and row['%K'] < 70
        and row['%K'] < row['%D']
    )


def generate_signal(symbol, interval):
    df = fetch_data(symbol, interval)
    if df is None or len(df) < 50:
        return None

    df = calculate_indicators(df)
    latest = df.iloc[-1]

    if check_buy_condition(latest):
        return {
            'symbol': symbol,
            'signal': 'BUY',
            'time': latest['time']
        }
    elif check_sell_condition(latest):
        return {
            'symbol': symbol,
            'signal': 'SELL',
            'time': latest['time']
        }

    return None
