"""
Deprecated: use 'preprocessing_feature_engineering.technical_indicators' instead.
This shim remains temporarily for backward compatibility.
"""
import warnings

warnings.filterwarnings("default", category=DeprecationWarning)
warnings.warn(
    "Importing from 'technical_indicators' is deprecated; "
    "use 'preprocessing_feature_engineering.technical_indicators' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from preprocessing_feature_engineering.technical_indicators import (
    TechnicalIndicatorGenerator,
    sma,
    ema,
    rsi,
)

__all__ = ["TechnicalIndicatorGenerator", "sma", "ema", "rsi"]
