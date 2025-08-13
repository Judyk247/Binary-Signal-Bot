# strategy.py
"""
Strategy module implementing:
- 5-min trend-reversal strategy (Alligator jaw=15, teeth=8, lips=5)
- Short-term trend-following strategies for 1/2/3 min
- Historical-bias, ATR volatility, fractals, EMA-150, stochastic (14,3,3)
- Sends Telegram alerts when a signal is found (reads TELEGRAM_TOKEN & TELEGRAM_CHAT_ID from env)

Functions:
 - evaluate_5min_reversal(df_5m) -> (signal, details)
 - evaluate_short_term_follow(df_tf, timeframe) -> (signal, details)
 - evaluate_pair_for_timeframes(df_1m) -> {1:...,2:...,3:...,5:...}
 - scan_and_alert(symbol, df_1m) -> sends telegram message if any timeframe signals
"""

from typing import Tuple, Optional, Dict, Any
import os
import time
import pandas as pd
import numpy as np
from datetime import datetime
from telegram_utils import send_telegram_alert  # external helper (uses .env)
# Soft import to acknowledge integration with your fetching layer
try:
    import data_fetcher  # noqa: F401
except Exception:
    data_fetcher = None

# --------------------------
# Settings & symbols list
# --------------------------
# 50 popular OTC currency pairs (major + minors)
CURRENCY_PAIRS = [
    "EUR/USD","GBP/USD","USD/JPY","USD/CHF","AUD/USD","USD/CAD","NZD/USD",
    "EUR/GBP","EUR/JPY","GBP/JPY","AUD/JPY","CHF/JPY","CAD/JPY","EUR/AUD",
    "EUR/CAD","GBP/CAD","GBP/CHF","AUD/CAD","AUD/CHF","NZD/JPY","NZD/CAD",
    "USD/SGD","USD/HKD","USD/TRY","EUR/TRY","GBP/TRY","USD/ZAR","EUR/NZD",
    "GBP/AUD","CAD/CHF","SEK/JPY","NOK/JPY","DKK/JPY","EUR/SEK","EUR/NOK",
    "USD/MXN","USD/INR","EUR/PLN","USD/PLN","EUR/CZK","USD/CZK","GBP/PLN",
    "GBP/NZD","AUD/NZD","CHF/SGD","EUR/SGD","GBP/SGD","NZD/CHF","CAD/NZD",
    "USD/ILS"
]

# Internal: prevent duplicate alerts per (symbol, timeframe, candle_close)
_SENT_ALERT_KEYS: set = set()

# --------------------------
# Indicator helpers
# --------------------------
def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()

def smma(series: pd.Series, period: int) -> pd.Series:
    """Simple SMMA (Wilder-style)."""
    s = series.copy().fillna(method="ffill")
    out = pd.Series(index=s.index, dtype=float)
    if len(s) < period:
        return out.fillna(np.nan)
    out.iloc[period - 1] = s.iloc[:period].mean()
    for i in range(period, len(s)):
        prev = out.iloc[i - 1]
        out.iloc[i] = (prev * (period - 1) + s.iloc[i]) / period
    return out

def alligator_lines(df: pd.DataFrame, jaw_p=15, teeth_p=8, lips_p=5):
    jaw = smma(df['close'], jaw_p)
    teeth = smma(df['close'], teeth_p)
    lips = smma(df['close'], lips_p)
    return jaw, teeth, lips

def stochastic(df: pd.DataFrame, k_period=14, d_period=3):
    low_min = df['low'].rolling(k_period, min_periods=1).min()
    high_max = df['high'].rolling(k_period, min_periods=1).max()
    k = 100 * (df['close'] - low_min) / (high_max - low_min + 1e-12)
    k_smooth = k.rolling(3, min_periods=1).mean()  # %K smooth
    d = k_smooth.rolling(3, min_periods=1).mean()
    return k_smooth, d

def atr(df: pd.DataFrame, period=14):
    prev_close = df['close'].shift(1)
    tr1 = df['high'] - df['low']
    tr2 = (df['high'] - prev_close).abs()
    tr3 = (df['low'] - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(period, min_periods=1).mean()

def volume_ma(df: pd.DataFrame, period=20):
    if 'volume' not in df:
        return pd.Series(0, index=df.index)
    return df['volume'].rolling(period, min_periods=1).mean()

# --------------------------
# Fractal detection
# --------------------------
def fractals(df: pd.DataFrame):
    """Return boolean Series (bullish_fractal, bearish_fractal)."""
    bullish = (df['low'].shift(2) > df['low']) & (df['low'].shift(1) > df['low']) & \
              (df['low'].shift(-1) > df['low']) & (df['low'].shift(-2) > df['low'])
    bearish = (df['high'].shift(2) < df['high']) & (df['high'].shift(1) < df['high']) & \
              (df['high'].shift(-1) < df['high']) & (df['high'].shift(-2) < df['high'])
    return bullish.fillna(False), bearish.fillna(False)

# --------------------------
# Helper: pivot midpoint (S/R proxy)
# --------------------------
def pivot_midpoint(df: pd.DataFrame, window=30):
    high = df['high'].rolling(window, min_periods=1).max()
    low = df['low'].rolling(window, min_periods=1).min()
    return (high + low) / 2

# --------------------------
# Historical bias / zone reversal checker
# --------------------------
def historical_bias_winrate(df: pd.DataFrame, idx: int, direction: str,
                            lookback_window: int = 50, search_window: int = 500,
                            future_horizon: int = 6, win_atr_mult: float = 0.5) -> Dict[str, Any]:
    """
    Scan past for similar pivot zone occurrences and measure quick wins in the given direction.
    Returns {matches, wins, win_rate}.
    """
    n = len(df)
    if n < 10 or idx < 1:
        return {"matches": 0, "wins": 0, "win_rate": 0.0}
    zone_value = pivot_midpoint(df, window=lookback_window).iloc[idx]
    atr_s = atr(df)
    ref_atr = atr_s.iloc[max(0, idx - 1)]
    if pd.isna(zone_value) or ref_atr == 0 or pd.isna(ref_atr):
        return {"matches": 0, "wins": 0, "win_rate": 0.0}

    matches = wins = 0
    start = max(5, idx - search_window)
    for i in range(start, idx - 5):
        hist_close = df['close'].iloc[i]
        if abs(hist_close - zone_value) <= (0.6 * ref_atr):
            matches += 1
            fut = df['close'].iloc[i + 1: min(n, i + 1 + future_horizon)]
            if fut.empty:
                continue
            atr_i = atr_s.iloc[i]
            if direction == "BUY":
                if (fut.max() - hist_close) >= (win_atr_mult * atr_i):
                    wins += 1
            else:
                if (hist_close - fut.min()) >= (win_atr_mult * atr_i):
                    wins += 1
    win_rate = (wins / matches) if matches > 0 else 0.0
    return {"matches": matches, "wins": wins, "win_rate": win_rate}

# --------------------------
# Last-3 candle confirmation checks
# --------------------------
def last3_reversal_check(df: pd.DataFrame, direction: str) -> bool:
    """
    Reversal 3-candle pattern as described in the spec.
    Expects df length >= 3 and df indexed ascending.
    """
    if len(df) < 3:
        return False
    c1 = df.iloc[-3]
    c2 = df.iloc[-2]
    c3 = df.iloc[-1]

    avg_body = df['close'].diff().abs().rolling(20, min_periods=1).mean().iloc[-1]
    avg_body = avg_body if avg_body > 0 else 1e-8

    def body_size(c): return abs(c['close'] - c['open'])
    def small_body(c): return body_size(c) <= 0.35 * avg_body
    def strong_bear(c): return (c['close'] < c['open']) and (body_size(c) >= 1.2 * avg_body)
    def strong_bull(c): return (c['close'] > c['open']) and (body_size(c) >= 1.2 * avg_body)

    if direction == "BUY":
        return bool(strong_bear(c1) and small_body(c2) and strong_bull(c3) and (c3['close'] > c2['high']))
    else:
        return bool(strong_bull(c1) and small_body(c2) and strong_bear(c3) and (c3['close'] < c2['low']))

def last3_trend_follow_check(df: pd.DataFrame, direction: str) -> bool:
    if len(df) < 3:
        return False
    c1 = df.iloc[-3]
    c2 = df.iloc[-2]
    c3 = df.iloc[-1]

    avg_body = df['close'].diff().abs().rolling(20, min_periods=1).mean().iloc[-1]
    avg_body = avg_body if avg_body > 0 else 1e-8
    small = lambda c: abs(c['close'] - c['open']) <= 0.45 * avg_body
    strong = lambda c: abs(c['close'] - c['open']) >= 1.1 * avg_body

    if direction == "BUY":
        cond1 = (c1['close'] < c1['open'])
        cond2 = small(c2)
        cond3 = strong(c3) and (c3['close'] > c2['high'])
        return bool(cond1 and cond2 and cond3)
    else:
        cond1 = (c1['close'] > c1['open'])
        cond2 = small(c2)
        cond3 = strong(c3) and (c3['close'] < c2['low'])
        return bool(cond1 and cond2 and cond3)

# --------------------------
# 5-minute reversal evaluator
# --------------------------
def evaluate_5min_reversal(df: pd.DataFrame,
                           atr_period: int = 14,
                           atr_median_window: int = 50,
                           hist_lookback: int = 50,
                           hist_search: int = 500,
                           hist_future: int = 6,
                           hist_win_atr_mult: float = 0.5) -> Tuple[Optional[str], Dict[str, Any]]:
    details: Dict[str, Any] = {"checks": {}, "mode": "TREND_REVERSAL", "timeframe": 5}
    if len(df) < 60:
        details['error'] = "insufficient_bars"
        return None, details

    dfc = df.copy()
    dfc['EMA150'] = ema(dfc['close'], 150)
    jaw, teeth, lips = alligator_lines(dfc, jaw_p=15, teeth_p=8, lips_p=5)
    dfc['jaw'], dfc['teeth'], dfc['lips'] = jaw, teeth, lips
    k, d = stochastic(dfc, 14, 3)
    dfc['K'], dfc['D'] = k, d
    dfc['ATR'] = atr(dfc, atr_period)
    dfc['ATR_median'] = dfc['ATR'].rolling(atr_median_window, min_periods=1).median()
    dfc['vol_ma20'] = volume_ma(dfc, 20)
    bull_fr, bear_fr = fractals(dfc)
    dfc['bull_fr'], dfc['bear_fr'] = bull_fr, bear_fr

    last = dfc.iloc[-1]
    last_idx = len(dfc) - 1

    # Pre-filters
    vol_ok = bool(last['ATR'] > dfc['ATR_median'].iloc[-1])
    details['checks']['volatility'] = vol_ok

    price_below_ema_a_while = (dfc['close'].iloc[-10:] < dfc['EMA150'].iloc[-10:]).sum() >= 6
    price_above_ema_a_while = (dfc['close'].iloc[-10:] > dfc['EMA150'].iloc[-10:]).sum() >= 6
    details['checks']['price_bias'] = {
        "below_count_last10": int((dfc['close'].iloc[-10:] < dfc['EMA150'].iloc[-10:]).sum()),
        "above_count_last10": int((dfc['close'].iloc[-10:] > dfc['EMA150'].iloc[-10:]).sum())
    }

    # Alligator contraction check
    range_now = abs(float(last['lips']) - float(last['jaw']))
    prev_mean_range = 0.0
    if len(dfc) > 20:
        prev_mean_range = abs(dfc['lips'].iloc[-20:-1].mean() - dfc['jaw'].iloc[-20:-1].mean())
    alligator_contract = bool(range_now < 0.75 * (prev_mean_range if prev_mean_range > 0 else range_now))
    details['checks']['alligator_contract'] = alligator_contract

    k_now = float(last['K'])
    k_prev = float(dfc['K'].iloc[-2]) if len(dfc) >= 2 else k_now
    details['checks']['stochastic'] = {"K_now": k_now, "K_prev": k_prev, "D_now": float(last['D'])}

    # BUY candidate
    buy_candidate = False
    if price_below_ema_a_while and alligator_contract and (k_now < 20 and k_prev <= k_now) and vol_ok:
        hb = historical_bias_winrate(dfc, last_idx, "BUY",
                                     lookback_window=hist_lookback,
                                     search_window=hist_search,
                                     future_horizon=hist_future,
                                     win_atr_mult=hist_win_atr_mult)
        details['checks']['historical_bias'] = hb
        last3_ok = last3_reversal_check(dfc, "BUY")
        details['checks']['last3'] = bool(last3_ok)
        if hb['matches'] >= 2 and hb['win_rate'] >= 0.25 and last3_ok:
            buy_candidate = True

    # SELL candidate
    sell_candidate = False
    if price_above_ema_a_while and alligator_contract and (k_now > 80 and k_prev >= k_now) and vol_ok:
        hb = historical_bias_winrate(dfc, last_idx, "SELL",
                                     lookback_window=hist_lookback,
                                     search_window=hist_search,
                                     future_horizon=hist_future,
                                     win_atr_mult=hist_win_atr_mult)
        details['checks']['historical_bias'] = hb
        last3_ok = last3_reversal_check(dfc, "SELL")
        details['checks']['last3'] = bool(last3_ok)
        if hb['matches'] >= 2 and hb['win_rate'] >= 0.25 and last3_ok:
            sell_candidate = True

    if buy_candidate:
        details.update({
            "signal": "BUY",
            "price": float(last['close']),
            "timestamp": str(dfc.index[-1]),
            "reason": "5m reversal BUY - all conditions met"
        })
        return "BUY", details

    if sell_candidate:
        details.update({
            "signal": "SELL",
            "price": float(last['close']),
            "timestamp": str(dfc.index[-1]),
            "reason": "5m reversal SELL - all conditions met"
        })
        return "SELL", details

    details.update({"signal": None, "reason": "No 5m reversal candidate"})
    return None, details

# --------------------------
# Short-term trend-follow evaluator (1/2/3 min)
# --------------------------
def evaluate_short_term_follow(df: pd.DataFrame, timeframe: int = 1,
                               atr_period: int = 14, atr_median_window: int = 30,
                               hist_lookback: int = 30, hist_search: int = 200,
                               hist_future: int = 4, hist_win_atr_mult: float = 0.4) -> Tuple[Optional[str], Dict]:
    details: Dict[str, Any] = {"checks": {}, "mode": "TREND_FOLLOW", "timeframe": timeframe}
    if len(df) < 40:
        details['error'] = "insufficient_bars"
        return None, details

    dfc = df.copy()
    dfc['EMA150'] = ema(dfc['close'], 150)
    jaw, teeth, lips = alligator_lines(dfc, jaw_p=15, teeth_p=8, lips_p=5)
    dfc['jaw'], dfc['teeth'], dfc['lips'] = jaw, teeth, lips
    k, d = stochastic(dfc, 14, 3)
    dfc['K'], dfc['D'] = k, d
    dfc['ATR'] = atr(dfc, atr_period)
    dfc['ATR_med30'] = dfc['ATR'].rolling(atr_median_window, min_periods=1).median()
    dfc['vol_ma20'] = volume_ma(dfc, 20)

    last = dfc.iloc[-1]
    last_idx = len(dfc) - 1

    # EMA slope
    ema_slope = float(dfc['EMA150'].iloc[-1] - dfc['EMA150'].iloc[-6]) if len(dfc) > 6 else 0.0
    trending_up = ema_slope > 0
    trending_down = ema_slope < 0
    details['checks']['ema_slope'] = ema_slope

    # ATR volatility filter
    vol_ok = last['ATR'] >= 0.5 * dfc['ATR_med30'].iloc[-1]
    details['checks']['vol_ok'] = bool(vol_ok)

    vol_strength = ('volume' in dfc.columns) and (last['volume'] >= dfc['vol_ma20'].iloc[-1])
    details['checks']['volume_strength'] = {"now": float(last['volume']) if 'volume' in dfc.columns else None,
                                            "ma20": float(dfc['vol_ma20'].iloc[-1])}

    buy_candidate = False
    if trending_up and last['close'] > last['EMA150'] and (last['lips'] > last['teeth'] > last['jaw']) and vol_ok and vol_strength:
        k_now = float(last['K']); k_prev = float(dfc['K'].iloc[-2]) if len(dfc) >= 2 else k_now
        cond_stoch = (k_now > k_prev) and (20 <= k_now <= 50)
        if cond_stoch:
            hb = historical_bias_winrate(dfc, last_idx, "BUY",
                                         lookback_window=hist_lookback,
                                         search_window=hist_search,
                                         future_horizon=hist_future,
                                         win_atr_mult=hist_win_atr_mult)
            details['checks']['historical_bias'] = hb
            three_ok = last3_trend_follow_check(dfc, "BUY")
            details['checks']['last3'] = bool(three_ok)
            if three_ok and (hb['matches'] == 0 or hb['win_rate'] >= 0.45):
                buy_candidate = True

    sell_candidate = False
    if trending_down and last['close'] < last['EMA150'] and (last['lips'] < last['teeth'] < last['jaw']) and vol_ok and vol_strength:
        k_now = float(last['K']); k_prev = float(dfc['K'].iloc[-2]) if len(dfc) >= 2 else k_now
        cond_stoch = (k_now < k_prev) and (50 <= k_now <= 80)
        if cond_stoch:
            hb = historical_bias_winrate(dfc, last_idx, "SELL",
                                         lookback_window=hist_lookback,
                                         search_window=hist_search,
                                         future_horizon=hist_future,
                                         win_atr_mult=hist_win_atr_mult)
            details['checks']['historical_bias'] = hb
            three_ok = last3_trend_follow_check(dfc, "SELL")
            details['checks']['last3'] = bool(three_ok)
            if three_ok and (hb['matches'] == 0 or hb['win_rate'] >= 0.45):
                sell_candidate = True

    if buy_candidate:
        details.update({"signal": "BUY", "price": float(last['close']), "timestamp": str(dfc.index[-1]),
                        "reason": f"{details['timeframe']}m trend-follow BUY - EMA slope, alligator alignment, stochastic pullback+last3, volatility OK"})
        return "BUY", details
    if sell_candidate:
        details.update({"signal": "SELL", "price": float(last['close']), "timestamp": str(dfc.index[-1]),
                        "reason": f"{details['timeframe']}m trend-follow SELL - EMA slope, alligator alignment, stochastic pullback+last3, volatility OK"})
        return "SELL", details

    details.update({"signal": None, "reason": "no short-term follow candidate"})
    return None, details

# --------------------------
# Multi-timeframe wrapper
# --------------------------
def evaluate_pair_for_timeframes(df_1m: pd.DataFrame) -> Dict[int, Dict[str, Any]]:
    """
    Input: df_1m (1-minute OHLCV, ascending)
    Output: dict keyed by timeframe in minutes {1: {...}, 2: {...}, 3: {...}, 5: {...}}
    1/2/3m -> TREND_FOLLOW ; 5m -> TREND_REVERSAL
    """
    out = {}
    base = df_1m.sort_index().copy()
    for mins in (1, 2, 3, 5):
        if mins == 1:
            df_tf = base.copy()
        else:
            df_tf = base.resample(f"{mins}T").agg({
                'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last',
                'volume': 'sum'
            }).dropna()
        if len(df_tf) < 20:
            out[mins] = {"signal": None, "details": {"error": "insufficient_bars", "timeframe": mins,
                                                     "mode": "TREND_FOLLOW" if mins in (1,2,3) else "TREND_REVERSAL"}}
            continue
        if mins == 5:
            sig, det = evaluate_5min_reversal(df_tf)
        else:
            sig, det = evaluate_short_term_follow(df_tf, timeframe=mins)
        out[mins] = {"signal": sig, "details": det}
    return out

# --------------------------
# Scanner: evaluate and alert (alerts only in last 30s before close)
# --------------------------
def scan_and_alert(symbol: str, df_1m: pd.DataFrame, send_alerts: bool = True) -> Dict[int, Dict[str, Any]]:
    """
    Evaluate a single symbol across timeframes and optionally send telegram alerts.
    Alerts are sent only during the last 30 seconds before the current candle closes,
    and de-duplicated per (symbol, timeframe, candle_close).
    Returns the evaluation dict for each timeframe.
    """
    res = evaluate_pair_for_timeframes(df_1m)

    now = pd.Timestamp.utcnow()
    for mins, info in res.items():
        sig = info.get("signal")
        det = info.get("details", {})
        if sig is None:
            continue

        # Mode label for clarity in alerts
        mode = det.get("mode") or ("TREND_FOLLOW" if mins in (1, 2, 3) else "TREND_REVERSAL")

        # The timestamp stored in details is the bar's OPEN (pandas resample label='left')
        try:
            bar_open = pd.Timestamp(det.get("timestamp"))
        except Exception:
            # fallback: try last index from provided df
            bar_open = df_1m.index[-1] if len(df_1m) else now

        bar_close = bar_open + pd.Timedelta(minutes=mins)
        window_start = bar_close - pd.Timedelta(seconds=30)

        # Only send inside the last 30 seconds before this candle closes
        if not (window_start <= now <= bar_close):
            continue

        # Deduplicate per (symbol, timeframe, bar_close)
        alert_key = (symbol, mins, str(bar_close))
        if alert_key in _SENT_ALERT_KEYS:
            continue
        _SENT_ALERT_KEYS.add(alert_key)

        price = det.get("price")
        reason = det.get("reason", "")
        msg = (
            f"📊 SIGNAL ({sig})\n"
            f"Pair: {symbol}\n"
            f"Mode: {mode}\n"
            f"TF: {mins}m\n"
 
