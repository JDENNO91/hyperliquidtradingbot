from typing import List, Dict, Any
import pandas as pd
import ta


def calculate_rsi(data: List[Dict[str, Any]], period: int):
    closes = [float(candle["c"]) for candle in data]
    series = pd.Series(closes)
    if len(series) < period:
        return None
    rsi_series = ta.momentum.RSIIndicator(series, window=period).rsi()
    latest_rsi = rsi_series.dropna().iloc[-1] if not rsi_series.dropna().empty else None
    return None if pd.isna(latest_rsi) else latest_rsi

def calculate_adx(data: List[Dict[str, Any]], period: int):
    df = pd.DataFrame({
        "high": [float(c["h"]) for c in data],
        "low": [float(c["l"]) for c in data],
        "close": [float(c["c"]) for c in data],
    })
    if len(df) < period:
        return {"adx": None, "plus_di": None, "minus_di": None}
    adx_indicator = ta.trend.ADXIndicator(df["high"], df["low"], df["close"], window=period)
    adx_series = adx_indicator.adx()
    plus_di_series = adx_indicator.adx_pos()
    minus_di_series = adx_indicator.adx_neg()

    return {
        "adx": adx_series.dropna().iloc[-1] if not adx_series.dropna().empty else None,
        "plus_di": plus_di_series.dropna().iloc[-1] if not plus_di_series.dropna().empty else None,
        "minus_di": minus_di_series.dropna().iloc[-1] if not minus_di_series.dropna().empty else None
    }

def calculate_bollinger_bands(data: List[Dict[str, Any]], period: int, std_dev: float):
    closes = [float(candle["c"]) for candle in data]
    if len(closes) < period:
        return {"lower": None, "middle": None, "upper": None}

    bb = ta.volatility.BollingerBands(pd.Series(closes), window=period, window_dev=std_dev)
    lower_band = bb.bollinger_lband().iloc[-1]
    middle_band = bb.bollinger_mavg().iloc[-1]
    upper_band = bb.bollinger_hband().iloc[-1]

    if pd.isna(lower_band) or pd.isna(middle_band) or pd.isna(upper_band):
        return {"lower": None, "middle": None, "upper": None}

    return {
        "lower": lower_band,
        "middle": middle_band,
        "upper": upper_band,
    }

__all__ = ["calculate_rsi", "calculate_adx", "calculate_bollinger_bands"]
