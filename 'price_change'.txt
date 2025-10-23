import requests

def get_top_usdt_spot_coins(n=10, min_volume=100000):
    url = "https://api.bitget.com/api/spot/v1/market/tickers"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        coins = []
        for ticker in data.get('data', []):
            symbol = ticker.get('symbol', '')
            # Use 'usdtVol' if available, otherwise 'quoteVol'
            volume = float(ticker.get('usdtVol', ticker.get('quoteVol', 0)))
            price_change = float(ticker.get('change', 0))
            # Only pairs ending with USDT (spot market)
            if symbol.endswith('USDT') and volume > min_volume:
                coins.append({
                    'symbol': symbol,
                    'volume': volume,
                    'price_change': price_change
                })
        coins = sorted(coins, key=lambda x: (x['volume'], abs(x['price_change'])), reverse=True)
        return coins[:n]
    except Exception as e:
        print("Error fetching Bitget data:", e)
        return []

if __name__ == "__main__":
    num_coins = 10
    min_vol = 100000
    print(f"Fetching top {num_coins} USDT spot coins with volume > {min_vol}...")
    coins = get_top_usdt_spot_coins(num_coins, min_vol)
    if coins:
        print("\nTop USDT Spot Coins on Bitget:")
        print(f"{'Symbol':15} {'Volume':>15} {'24h Change':>12}")
        print("-"*45)
        for coin in coins:
            print(f"{coin['symbol']:15} {coin['volume']:15,.0f} {coin['price_change']:12.2f}")
    else:
        print("No coins found with that criteria.")