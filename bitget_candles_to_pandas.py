import requests

def get_candles(symbol='BTCUSDT', period='1h', limit=100):
    url = "https://api.bitget.com/api/spot/v1/market/history-candles"
    params = {
        'symbol': symbol,
        'period': period,   # '1m', '5m', '15m', '1h', '4h', '1d'
        'limit': limit
    }
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()
    return data.get('data', [])

# Example usage:
candles = get_candles('BTCUSDT', '1h', 100)
for row in candles[:5]:
    print(row)  # [timestamp, open, high, low, close, volume]