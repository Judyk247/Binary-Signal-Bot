# utils.py
import pandas as pd
import numpy as np

# ==============================
# Indicator Calculations
# ==============================

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def alligator(df, jaw=15, teeth=8, lips=5):
    df['alligator_jaw'] = df['close'].shift(jaw) \
        .rolling(window=jaw).mean()
    df['alligator_teeth'] = df['close'].shift(teeth) \
        .rolling(window=teeth).mean()
    df['alligator_lips'] = df['close'].shift(lips) \
        .rolling(window=lips).mean()
    return df

def stochastic(df, k_period=14, d_period=3, slowing=3):
    low_min = df['low'].rolling(window=k_period).min()
    high_max = df['high'].rolling(window=k_period).max()
    df['%K'] = ((df['close'] - low_min) / (high_max - low_min)) * 100
    df['%D'] = df['%K'].rolling(window=d_period).mean()
    return df

def atr(df, period=14):
    df['H-L'] = df['high'] - df['low']
    df['H-C'] = abs(df['high'] - df['close'].shift(1))
    df['L-C'] = abs(df['low'] - df['close'].shift(1))
    tr = df[['H-L', 'H-C', 'L-C']].max(axis=1)
    df['ATR'] = tr.rolling(window=period).mean()
    return df

def fractals(df):
    df['fractal_high'] = df['high'][(df['high'].shift(2) < df['high'].shift(0)) &
                                    (df['high'].shift(1) < df['high'].shift(0)) &
                                    (df['high'].shift(-1) < df['high'].shift(0)) &
                                    (df['high'].shift(-2) < df['high'].shift(0))]
    df['fractal_low'] = df['low'][(df['low'].shift(2) > df['low'].shift(0)) &
                                  (df['low'].shift(1) > df['low'].shift(0)) &
                                  (df['low'].shift(-1) > df['low'].shift(0)) &
                                  (df['low'].shift(-2) > df['low'].shift(0))]
    return df

# ==============================
# Price Action & Structure
# ==============================

def detect_support_resistance(df, lookback=50):
    levels = []
    for i in range(lookback, len(df)-lookback):
        high = df['high'][i]
        low = df['low'][i]
        if high == max(df['high'][i-lookback:i+lookback]):
            levels.append((i, high))
        elif low == min(df['low'][i-lookback:i+lookback]):
            levels.append((i, low))
    return levels

def historical_bias(df, zone_price, tolerance=0.002, min_hits=2, lookback=50):
    hits = 0
    for i in range(-lookback, -1):
        if abs(df['close'].iloc[i] - zone_price) / zone_price <= tolerance:
            hits += 1
    return hits >= min_hits

# ==============================
# Candle Pattern Confirmation
# ==============================

def check_three_candle_reversal(df):
    """
    Returns 'bullish' or 'bearish' if 3-candle reversal pattern detected
    """
    c1 = df.iloc[-3]
    c2 = df.iloc[-2]
    c3 = df.iloc[-1]

    # Bullish reversal
    if (c1['close'] < c1['open'] and  # Strong bearish
        abs(c2['close'] - c2['open']) <= (c1['high'] - c1['low']) * 0.3 and  # Small body
        c3['close'] > c2['high'] and  # Strong bullish close above c2
        c3['close'] > c3['open']):
        return 'bullish'

    # Bearish reversal
    if (c1['close'] > c1['open'] and  # Strong bullish
        abs(c2['close'] - c2['open']) <= (c1['high'] - c1['low']) * 0.3 and  # Small body
        c3['close'] < c2['low'] and  # Strong bearish close below c2
        c3['close'] < c3['open']):
        return 'bearish'

    return None

# ==============================
# Volatility Filter
# ==============================

def volatility_ok(df, atr_period=14, median_period=50, threshold=1.0):
    median_atr = df['ATR'].rolling(window=median_period).median().iloc[-1]
    return df['ATR'].iloc[-1] > median_atr * threshold
