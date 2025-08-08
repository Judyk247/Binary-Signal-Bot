# indicators.py

import pandas as pd
import numpy as np


def calculate_ema(df, period=150):
    df['EMA'] = df['close'].ewm(span=period, adjust=False).mean()
    return df


def calculate_alligator(df):
    df['Jaw'] = df['close'].rolling(window=13).mean().shift(8)
    df['Teeth'] = df['close'].rolling(window=8).mean().shift(5)
    df['Lips'] = df['close'].rolling(window=5).mean().shift(3)
    return df


def calculate_stochastic(df, k_period=14, d_period=3):
    low_min = df['low'].rolling(window=k_period).min()
    high_max = df['high'].rolling(window=k_period).max()
    df['%K'] = 100 * ((df['close'] - low_min) / (high_max - low_min))
    df['%D'] = df['%K'].rolling(window=d_period).mean()
    return df


def calculate_heikin_ashi(df):
    ha_df = df.copy()
    ha_df['HA_close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4

    ha_open = [(df['open'][0] + df['close'][0]) / 2]
    for i in range(1, len(df)):
        ha_open.append((ha_open[i - 1] + ha_df['HA_close'][i - 1]) / 2)
    ha_df['HA_open'] = ha_open

    ha_df['HA_high'] = ha_df[['HA_open', 'HA_close', 'high']].max(axis=1)
    ha_df['HA_low'] = ha_df[['HA_open', 'HA_close', 'low']].min(axis=1)

    return ha_df[['HA_open', 'HA_high', 'HA_low', 'HA_close']]


def is_bullish_momentum(df, candle_count=3):
    candles = df.tail(candle_count)
    bullish = all(row['HA_close'] > row['HA_open'] for _, row in candles.iterrows())
    strong_body = all((row['HA_close'] - row['HA_open']) > ((row['HA_high'] - row['HA_low']) * 0.5)
                      for _, row in candles.iterrows())
    return bullish and strong_body


def is_bearish_momentum(df, candle_count=3):
    candles = df.tail(candle_count)
    bearish = all(row['HA_close'] < row['HA_open'] for _, row in candles.iterrows())
    strong_body = all((row['HA_open'] - row['HA_close']) > ((row['HA_high'] - row['HA_low']) * 0.5)
                      for _, row in candles.iterrows())
    return bearish and strong_body
