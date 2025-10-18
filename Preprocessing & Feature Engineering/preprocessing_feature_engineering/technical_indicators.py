import pandas as pd
import pandas_ta as ta
from typing import Dict, List

class TechnicalIndicatorGenerator:
    def __init__(self):
        self.indicators = {
            'sma': self._calculate_sma,
            'ema': self._calculate_ema,
            'rsi': self._calculate_rsi,
            'macd': self._calculate_macd,
            'bollinger_bands': self._calculate_bollinger_bands,
            'atr': self._calculate_atr
        }
    
    def _calculate_sma(self, data: pd.DataFrame, period: int = 20) -> pd.Series:
        return data['close'].rolling(window=period).mean()
    
    def _calculate_ema(self, data: pd.DataFrame, period: int = 20) -> pd.Series:
        return data['close'].ewm(span=period).mean()
    
    def _calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        return ta.rsi(data['close'], length=period)
    
    def _calculate_macd(self, data: pd.DataFrame) -> pd.DataFrame:
        return ta.macd(data['close'])
    
    def _calculate_bollinger_bands(self, data: pd.DataFrame, period: int = 20, std: int = 2) -> pd.DataFrame:
        return ta.bbands(data['close'], length=period, std=std)
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        return ta.atr(data['high'], data['low'], data['close'], length=period)
    
    def generate_indicators(self, data: pd.DataFrame, indicators: List[str], **params) -> Dict[str, pd.Series]:
        results = {}
        for indicator in indicators:
            if indicator in self.indicators:
                results[indicator] = self.indicators[indicator](data, **params.get(indicator, {}))
        return results
