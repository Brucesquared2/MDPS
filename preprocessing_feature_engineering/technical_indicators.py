"""
Technical indicators module with SMA, EMA, and RSI plus a generator class.

Usage:
    import pandas as pd
    from preprocessing_feature_engineering import TechnicalIndicatorGenerator

    df = pd.read_csv("data.csv", parse_dates=True, index_col=0)
    gen = TechnicalIndicatorGenerator(price_col="Close")
    out = gen.generate_indicators(df, params={"sma": {"window": 20}, "ema": {"window": 50}, "rsi": {"window": 14}})
    out_df = gen.generate_dataframe(df, params={"sma": {"window": 20}, "ema": {"window": 50}, "rsi": {"window": 14}})
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Mapping, Optional

import numpy as np
import pandas as pd


__all__ = ["sma", "ema", "rsi", "TechnicalIndicatorGenerator"]

def _ensure_series_numeric(series: pd.Series, name: str = "series") -> pd.Series:
    """Ensure the input is a float Series with aligned index."""
    if not isinstance(series, pd.Series):
        raise TypeError(f"{name} must be a pandas Series.")
    try:
        series = pd.to_numeric(series, errors="coerce")
    except Exception as exc:
        raise ValueError(f"Unable to convert {name} to numeric dtype") from exc
    return series.astype("float64")

def _validate_window(window: int) -> None:
    if not isinstance(window, int) or window <= 0:
        raise ValueError("window must be a positive integer")

def sma(series: pd.Series, window: int = 14, min_periods: Optional[int] = None) -> pd.Series:
    """
    Simple Moving Average.
    """
    _validate_window(window)
    series = _ensure_series_numeric(series, "series")
    mp = window if min_periods is None else min_periods
    return series.rolling(window=window, min_periods=mp).mean()

def ema(series: pd.Series, window: int = 14) -> pd.Series:
    """
    Exponential Moving Average.
    """
    _validate_window(window)
    series = _ensure_series_numeric(series, "series")
    return series.ewm(span=window, adjust=False).mean()

def rsi(series: pd.Series, window: int = 14, method: str = "wilders") -> pd.Series:
    """
    Relative Strength Index.
    """
    _validate_window(window)
    series = _ensure_series_numeric(series, "series")

    delta = series.diff()
    gains = delta.clip(lower=0.0)
    losses = -delta.clip(upper=0.0)

    if method.lower() == "wilders":
        avg_gain = gains.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
        avg_loss = losses.ewm(alpha=1 / window, adjust=False, min_periods=window).mean()
    elif method.lower() == "sma":
        avg_gain = gains.rolling(window=window, min_periods=window).mean()
        avg_loss = losses.rolling(window=window, min_periods=window).mean()
    else:
        raise ValueError("method must be 'wilders' or 'sma'")

    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    rsi_vals = 100 - (100 / (1 + rs))
    return rsi_vals.clip(lower=0, upper=100).fillna(0.0)

class TechnicalIndicatorGenerator:
    """
    Minimal technical indicator generator.
    """

    def __init__(self, price_col: str = "Close"):
        self.price_col = price_col
        self.indicators: Dict[str, Callable[..., pd.Series]] = {
            "sma": lambda df, **kw: sma(df[self.price_col], **kw),
            "ema": lambda df, **kw: ema(df[self.price_col], **kw),
            "rsi": lambda df, **kw: rsi(df[self.price_col], **kw),
        }

    def register_indicator(self, name: str, func: Callable[..., pd.Series]) -> None:
        if not callable(func):
            raise TypeError("func must be callable")
        if not isinstance(name, str) or not name:
            raise ValueError("name must be a non-empty string")
        self.indicators[name] = func

    def _ensure_price_col(self, data: pd.DataFrame) -> None:
        if self.price_col not in data.columns:
            raise KeyError(f"price_col '{self.price_col}' not found in DataFrame columns")

    def generate_indicators(
        self,
        data: pd.DataFrame,
        params: Optional[Mapping[str, Mapping[str, Any]]] = None,
    ) -> Dict[str, pd.Series]:
        self._ensure_price_col(data)
        params = {} if params is None else dict(params)
        results: Dict[str, pd.Series] = {}

        for name, func in self.indicators.items():
            try:
                kwargs = params.get(name, {}) or {}
                series = func(data, **kwargs)
                if not isinstance(series, pd.Series):
                    raise TypeError(f"Indicator '{name}' must return a pandas Series")
                results[name] = series.reindex(data.index)
            except Exception:
                results[name] = pd.Series(np.nan, index=data.index, dtype="float64")

        return results

    def generate_dataframe(
        self,
        data: pd.DataFrame,
        params: Optional[Mapping[str, Mapping[str, Any]]] = None,
        column_suffix: Optional[str] = None,
    ) -> pd.DataFrame:
        results = self.generate_indicators(data, params=params)
        if column_suffix:
            results = {f"{k}_{column_suffix}": v for k, v in results.items()}
        return pd.DataFrame(results, index=data.index)