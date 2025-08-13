# signals.py
import pandas as pd
import talib
from typing import Dict

# ==============================
# Indicator Calculation Helpers
# ==============================

def calculate_alligator(df: pd.DataFrame, jaw=15, teeth=8, lips=5) -> pd.DataFrame:
    df["jaw"] = df["close"].shift(jaw).rolling(jaw).mean()
    df["teeth"] = df["close"].shift(teeth).rolling(teeth).mean()
    df["lips"] = df["close"].shift(lips).rolling(lips).mean()
    return df

def calculate_fractals(df: pd.DataFrame) -> pd.DataFrame:
    df["fractal_high"] = df["high"].shift(2) > df["high"].shift(3)
    df["fractal_low"] = df["low"].shift(2) < df["low"].shift(3)
    return df

def calculate_stochastic(df: pd.DataFrame, k_period=14, d_period=3, slowing=3):
    k, d = talib.STOCH(
        df["high"], df["low"], df["close"],
        fastk_period=k_period,
        slowk_period=slowing,
        slowd_period=d_period,
        slowk_matype=0,
        slowd_matype=0
    )
    df["stoch_k"], df["stoch_d"] = k, d
    return df

def calculate_ema(df: pd.DataFrame, period=150):
    df[f"ema_{period}"] = talib.EMA(df["close"], timeperiod=period)
    return df

def calculate_atr(df: pd.DataFrame, period=14):
    df["atr"] = talib.ATR(df["high"], df["low"], df["close"], timeperiod=period)
    return df

# ==============================
# Strategy Conditions
# ==============================

def check_5m_trend_reversal(df: pd.DataFrame) -> Dict:
    """Returns signal dict for 5-minute trend reversal strategy"""
    last = df.iloc[-1]
    last3 = df.iloc[-3:]

    signals = {"buy": False, "sell": False}

    # BUY Conditions
    if (
        last["close"] < last[f"ema_150"] and
        last["stoch_k"] < 20 and last["stoch_k"] > last["stoch_d"] and
        last["atr"] > df["atr"].rolling(50).median().iloc[-1] and
        last3.iloc[0]["close"] < last3.iloc[0]["open"] and  # bearish
        abs(last3.iloc[1]["close"] - last3.iloc[1]["open"]) / last3.iloc[1]["close"] < 0.0015 and  # indecision
        last3.iloc[2]["close"] > last3.iloc[1]["high"]  # bullish breakout
    ):
        signals["buy"] = True

    # SELL Conditions
    if (
        last["close"] > last[f"ema_150"] and
        last["stoch_k"] > 80 and last["stoch_k"] < last["stoch_d"] and
        last["atr"] > df["atr"].rolling(50).median().iloc[-1] and
        last3.iloc[0]["close"] > last3.iloc[0]["open"] and  # bullish
        abs(last3.iloc[1]["close"] - last3.iloc[1]["open"]) / last3.iloc[1]["close"] < 0.0015 and  # indecision
        last3.iloc[2]["close"] < last3.iloc[1]["low"]  # bearish breakout
    ):
        signals["sell"] = True

    return signals


def check_trend_following(df: pd.DataFrame, tf_label: str) -> Dict:
    """Returns signal dict for 1m, 2m, 3m trend-following strategy"""
    last = df.iloc[-1]
    last3 = df.iloc[-3:]

    signals = {"buy": False, "sell": False}

    # BUY
    if (
        last["close"] > last["ema_150"] and
        last["lips"] > last["teeth"] > last["jaw"] and
        last["stoch_k"] > last["stoch_d"] and
        last["stoch_k"] > 20 and
        last3.iloc[0]["close"] < last3.iloc[0]["open"] and
        abs(last3.iloc[1]["close"] - last3.iloc[1]["open"]) / last3.iloc[1]["close"] < 0.0015 and
        last3.iloc[2]["close"] > last3.iloc[1]["high"]
    ):
        signals["buy"] = True

    # SELL
    if (
        last["close"] < last["ema_150"] and
        last["lips"] < last["teeth"] < last["jaw"] and
        last["stoch_k"] < last["stoch_d"] and
        last["stoch_k"] < 80 and
        last3.iloc[0]["close"] > last3.iloc[0]["open"] and
        abs(last3.iloc[1]["close"] - last3.iloc[1]["open"]) / last3.iloc[1]["close"] < 0.0015 and
        last3.iloc[2]["close"] < last3.iloc[1]["low"]
    ):
        signals["sell"] = True

    return signals

# ==============================
# Main Signal Dispatcher
# ==============================

def generate_signals(df: pd.DataFrame, timeframe: str) -> Dict:
    """
    Runs indicator calculations & returns signals
    timeframe: '1m', '2m', '3m' = trend following
               '5m' = trend reversal
    """
    df = calculate_alligator(df)
    df = calculate_fractals(df)
    df = calculate_stochastic(df)
    df = calculate_ema(df)
    df = calculate_atr(df)

    if timeframe == "5m":
        return check_5m_trend_reversal(df)
    elif timeframe in ["1m", "2m", "3m"]:
        return check_trend_following(df, timeframe)
    else:
        return {"buy": False, "sell": False}
