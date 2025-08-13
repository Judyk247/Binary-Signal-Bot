# strategy.py
import pandas as pd
import numpy as np
from data_fetcher import fetch_data

# --- Indicator Calculations ---
def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def stochastic_kd(df, k_period=14, d_period=3):
    low_min = df['low'].rolling(window=k_period).min()
    high_max = df['high'].rolling(window=k_period).max()
    k = 100 * ((df['close'] - low_min) / (high_max - low_min))
    d = k.rolling(window=d_period).mean()
    return k, d

def alligator(df, jaw=13, teeth=8, lips=5):
    jaw_line = df['close'].rolling(window=jaw).mean().shift(8)
    teeth_line = df['close'].rolling(window=teeth).mean().shift(5)
    lips_line = df['close'].rolling(window=lips).mean().shift(3)
    return jaw_line, teeth_line, lips_line

def fractal(df):
    df['fractal_up'] = df['high'][(df['high'].shift(2) < df['high'].shift(0)) &
                                  (df['high'].shift(1) < df['high'].shift(0)) &
                                  (df['high'].shift(-1) < df['high'].shift(0)) &
                                  (df['high'].shift(-2) < df['high'].shift(0))]
    df['fractal_down'] = df['low'][(df['low'].shift(2) > df['low'].shift(0)) &
                                   (df['low'].shift(1) > df['low'].shift(0)) &
                                   (df['low'].shift(-1) > df['low'].shift(0)) &
                                   (df['low'].shift(-2) > df['low'].shift(0))]
    return df

# --- Strategy Implementations ---
def trend_following_strategy(symbol, interval):
    df = fetch_data(symbol, interval, 200)
    if df is None or df.empty:
        return None

    # Indicators
    df['ema150'] = ema(df['close'], 150)
    df['%K'], df['%D'] = stochastic_kd(df, 14, 3)
    df['jaw'], df['teeth'], df['lips'] = alligator(df)
    df = fractal(df)

    last = df.iloc[-1]

    # --- Buy condition ---
    if (last['close'] > last['ema150'] and
        last['close'] > last['jaw'] and last['close'] > last['teeth'] and last['close'] > last['lips'] and
        last['%K'] > last['%D'] and last['%K'] < 30):
        return f"[TREND FOLLOWING BUY] {symbol} {interval}"

    # --- Sell condition ---
    if (last['close'] < last['ema150'] and
        last['close'] < last['jaw'] and last['close'] < last['teeth'] and last['close'] < last['lips'] and
        last['%K'] < last['%D'] and last['%K'] > 70):
        return f"[TREND FOLLOWING SELL] {symbol} {interval}"

    return None

def trend_reversal_strategy(symbol):
    df = fetch_data(symbol, "5min", 200)
    if df is None or df.empty:
        return None

    # Indicators
    df['ema150'] = ema(df['close'], 150)
    df['%K'], df['%D'] = stochastic_kd(df, 14, 3)
    df['jaw'], df['teeth'], df['lips'] = alligator(df)
    df = fractal(df)

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # --- Bullish reversal ---
    if (prev['%K'] < 20 and last['%K'] > last['%D'] and
        last['close'] > last['jaw'] and last['close'] > last['teeth'] and last['close'] > last['lips']):
        return f"[TREND REVERSAL BUY] {symbol} 5min"

    # --- Bearish reversal ---
    if (prev['%K'] > 80 and last['%K'] < last['%D'] and
        last['close'] < last['jaw'] and last['close'] < last['teeth'] and last['close'] < last['lips']):
        return f"[TREND REVERSAL SELL] {symbol} 5min"

    return None

# --- Currency Pairs List ---
CURRENCY_PAIRS = [
    "EUR/USD", "USD/JPY", "GBP/USD", "USD/CHF", "AUD/USD",
    "USD/CAD", "NZD/USD", "EUR/GBP", "EUR/JPY", "GBP/JPY",
    "CHF/JPY", "EUR/AUD", "EUR/CAD", "EUR/CHF", "AUD/CAD",
    "AUD/CHF", "AUD/JPY", "CAD/CHF", "CAD/JPY", "NZD/JPY",
    "NZD/CAD", "NZD/CHF", "GBP/AUD", "GBP/CAD", "GBP/CHF",
    "GBP/NZD", "EUR/NZD", "USD/SEK", "USD/NOK", "USD/DKK",
    "USD/HKD", "USD/SGD", "USD/TRY", "USD/ZAR", "USD/INR",
    "USD/MXN", "USD/PLN", "USD/THB", "USD/CNH", "USD/KRW",
    "EUR/SEK", "EUR/NOK", "EUR/DKK", "EUR/TRY", "EUR/ZAR",
    "AUD/NZD", "AUD/SGD", "NZD/SGD", "GBP/SGD", "CHF/SGD"
]

# --- Main signal runner ---
def get_signals():
    signals = []
    for symbol in CURRENCY_PAIRS:
        # 1m, 2m, 3m trend-following
        for tf in ["1min", "2min", "3min"]:
            sig = trend_following_strategy(symbol, tf)
            if sig:
                signals.append(sig)

        # 5m trend-reversal
        sig = trend_reversal_strategy(symbol)
        if sig:
            signals.append(sig)

    return signals
