def get_recent_trades(symbol='BTCUSDT', limit=50):
    url = "https://api.bitget.com/api/spot/v1/market/fills"
    params = {'symbol': symbol, 'limit': limit}
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()
    return data.get('data', [])

trades = get_recent_trades()
for t in trades[:5]:
    print(t)