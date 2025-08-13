# indicators.py
import pandas as pd
import ta

def calculate_ema(df: pd.DataFrame, period: int = 150) -> pd.Series:
    """Calculate EMA for the given period."""
    return ta.trend.ema_indicator(df['close'], window=period)

def calculate_alligator(df: pd.DataFrame, jaw_period=15, teeth_period=8, lips_period=5) -> pd.DataFrame:
    """
    Alligator Indicator using smoothed moving averages shifted forward.
    Returns: DataFrame with jaw, teeth, lips columns.
    """
    jaw = df['close'].rolling(jaw_period).mean().shift(jaw_period // 2)
    teeth = df['close'].rolling(teeth_period).mean().shift(teeth_period // 2)
    lips = df['close'].rolling(lips_period).mean().shift(lips_period // 2)
    
    df['alligator_jaw'] = jaw
    df['alligator_teeth'] = teeth
    df['alligator_lips'] = lips
    return df

def calculate_stochastic(df: pd.DataFrame, k_period=14, d_period=3, smooth=3) -> pd.DataFrame:
    """Calculate Stochastic Oscillator."""
    low_min = df['low'].rolling(window=k_period).min()
    high_max = df['high'].rolling(window=k_period).max()
    stoch_k = 100 * (df['close'] - low_min) / (high_max - low_min)
    stoch_d = stoch_k.rolling(window=d_period).mean()

    df['stoch_k'] = stoch_k.rolling(window=smooth).mean()
    df['stoch_d'] = stoch_d
    return df

def calculate_atr(df: pd.DataFrame, period=14) -> pd.Series:
    """Calculate ATR."""
    atr_indicator = ta.volatility.AverageTrueRange(
        high=df['high'],
        low=df['low'],
        close=df['close'],
        window=period
    )
    return atr_indicator.average_true_range()

def calculate_fractals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify fractals (swing highs/lows).
    A fractal high is when the high is higher than 2 bars on each side.
    A fractal low is when the low is lower than 2 bars on each side.
    """
    df['fractal_high'] = df['high'][(df['high'].shift(2) < df['high']) &
                                    (df['high'].shift(1) < df['high']) &
                                    (df['high'].shift(-1) < df['high']) &
                                    (df['high'].shift(-2) < df['high'])]

    df['fractal_low'] = df['low'][(df['low'].shift(2) > df['low']) &
                                  (df['low'].shift(1) > df['low']) &
                                  (df['low'].shift(-1) > df['low']) &
                                  (df['low'].shift(-2) > df['low'])]
    return df

def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all indicators used in both strategies."""
    df['ema150'] = calculate_ema(df, 150)
    df = calculate_alligator(df)
    df = calculate_stochastic(df)
    df['atr14'] = calculate_atr(df)
    df = calculate_fractals(df)
    return df
