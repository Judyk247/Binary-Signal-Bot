# strategy.py

import pandas as pd
import numpy as np


def heikin_ashi(df):
    ha_df = df.copy()
    ha_df['HA_Close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4

    ha_open = [(df['open'][0] + df['close'][0]) / 2]
    for i in range(1, len(df)):
        ha_open.append((ha_open[i - 1] + ha_df['HA_Close'][i - 1]) / 2)
    ha_df['HA_Open'] = ha_open

    ha_df['HA_High'] = ha_df[['HA_Open', 'HA_Close', 'high']].max(axis=1)
    ha_df['HA_Low'] = ha_df[['HA_Open', 'HA_Close', 'low']].min(axis=1)

    return ha_df


def calculate_indicators(df):
    df['EMA150'] = df['close'].ewm(span=150, adjust=False).mean()

    jaw = df['close'].rolling(window=13).mean()
    teeth = df['close'].rolling(window=8).mean()
    lips = df['close'].rolling(window=5).mean()
    df['Alligator_Jaw'] = jaw
    df['Alligator_Teeth'] = teeth
    df['Alligator_Lips'] = lips

    low_k = df['low'].rolling(window=14).min()
    high_k = df['high'].rolling(window=14).max()
    df['%K'] = 100 * ((df['close'] - low_k) / (high_k - low_k + 1e-9))
    df['%D'] = df['%K'].rolling(window=3).mean()

    df['ATR'] = df['high'] - df['low']

    return df


def is_bullish_candle(row):
    return row['HA_Close'] > row['HA_Open']


def is_bearish_candle(row):
    return row['HA_Close'] < row['HA_Open']


def detect_buy_signal(df):
    recent = df.iloc[-1]
    prev = df.iloc[-2]
    past = df.iloc[-51:-1]  # last 50 candles

    if (
        recent['close'] > recent['EMA150'] and
        recent['close'] > recent['Alligator_Jaw'] and
        recent['close'] > recent['Alligator_Teeth'] and
        recent['close'] > recent['Alligator_Lips'] and
        recent['%K'] > 30 and
        recent['%K'] > recent['%D'] and
        is_bullish_candle(recent) and
        (past['HA_Close'] < past['HA_Open']).sum() > 10 and
        recent['ATR'] > past['ATR'].mean() * 0.8
    ):
        return True
    return False


def detect_sell_signal(df):
    recent = df.iloc[-1]
    prev = df.iloc[-2]
    past = df.iloc[-51:-1]  # last 50 candles

    if (
        recent['close'] < recent['EMA150'] and
        recent['close'] < recent['Alligator_Jaw'] and
        recent['close'] < recent['Alligator_Teeth'] and
        recent['close'] < recent['Alligator_Lips'] and
        recent['%K'] < 70 and
        recent['%K'] < recent['%D'] and
        is_bearish_candle(recent) and
        (past['HA_Close'] > past['HA_Open']).sum() > 10 and
        recent['ATR'] > past['ATR'].mean() * 0.8
    ):
        return True
    return False


def analyze_symbol(df):
    if len(df) < 60:
        return None

    df = calculate_indicators(df)
    df = heikin_ashi(df)

    if detect_buy_signal(df):
        return "Buy"
    elif detect_sell_signal(df):
        return "Sell"
    else:
        return None
