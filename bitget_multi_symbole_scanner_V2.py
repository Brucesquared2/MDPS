import requests

def get_top_usdt_spot_coins(n=10, min_volume=100000):
    url = "https://api.bitget.com/api/spot/v1/market/tickers"
    resp = requests.get(url, timeout=10)
    data = resp.json()
    coins = []
    for ticker in data.get('data', []):
        symbol = ticker.get('symbol', '')
        volume = float(ticker.get('usdtVol', ticker.get('quoteVol', 0)))
        if symbol.endswith('USDT') and volume > min_volume:
            coins.append(symbol)
    return coins[:n]

def get_candles(symbol='BTCUSDT', period='1h', limit=100):
    url = "https://api.bitget.com/api/spot/v1/market/history-candles"
    params = {'symbol': symbol, 'period': period, 'limit': limit}
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()
    return data.get('data', [])

if __name__ == "__main__":
    top_symbols = get_top_usdt_spot_coins(5, 100000)
    print("Top symbols:", top_symbols)
    for sym in top_symbols:
        candles = get_candles(sym, '1h', 10)
        print(f"\nCandles for {sym}:")
        for row in candles:
            print(row)