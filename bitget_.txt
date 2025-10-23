import requests
import pandas as pd

def get_candles(symbol='BTCUSDT', period='1h', limit=100):
    url = "https://api.bitget.com/api/spot/v1/market/history-candles"
    params = {'symbol': symbol, 'period': period, 'limit': limit}
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()
    return data.get('data', [])

candles = get_candles('BTCUSDT', '1h', 100)
df = pd.DataFrame(candles, columns=['ts', 'open', 'high', 'low', 'close', 'vol'])
df['close'] = df['close'].astype(float)
print(df.head())