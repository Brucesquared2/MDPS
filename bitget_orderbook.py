def get_orderbook(symbol='BTCUSDT', limit=10):
    url = "https://api.bitget.com/api/spot/v1/market/depth"
    params = {'symbol': symbol, 'limit': limit}
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()
    return data.get('data', {})

orderbook = get_orderbook('BTCUSDT')
print(orderbook)  # bids, asks