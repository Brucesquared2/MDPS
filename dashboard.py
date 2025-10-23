import requests

def get_top_usdtp_coins(n=10, min_volume=100000):
    url = "https://api.bitget.com/api/mix/v1/market/tickers?productType=USDT-FUTURES"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # Debug: Uncomment to see the raw response structure
        # print(data)
        if not data or 'data' not in data or not isinstance(data['data'], list):
            print("Bitget API returned invalid response:", data)
            return []
        coins = []
        for ticker in data['data']:
            symbol = ticker.get('symbol', '')
            volume = float(ticker.get('quoteVolume', 0))
            price_change = float(ticker.get('change24h', 0))
            # Adjust the filter if needed based on symbol format
            if symbol.endswith('USDT.P') and volume > min_volume:
                coins.append({
                    'symbol': symbol,
                    'volume': volume,
                    'price_change': price_change
                })
        coins = sorted(coins, key=lambda x: (x['volume'], x['price_change']), reverse=True)
        return coins[:n]
    except Exception as e:
        print("Error fetching Bitget data:", e)
        return []

if __name__ == "__main__":
    num_coins = 10
    min_vol = 100000
    print(f"Fetching top {num_coins} USDT.P coins with volume > {min_vol}...")
    coins = get_top_usdtp_coins(num_coins, min_vol)
    if coins:
        print("\nTop USDT.P Perpetual Coins on Bitget:")
        print(f"{'Symbol':15} {'Volume':>15} {'24h Change':>12}")
        print("-"*45)
        for coin in coins:
            print(f"{coin['symbol']:15} {coin['volume']:15,.0f} {coin['price_change']:12.2f}")
    else:
        print("No coins found with that criteria.")