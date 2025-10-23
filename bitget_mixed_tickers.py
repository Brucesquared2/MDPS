import requests

url = "https://api.bitget.com/api/spot/v1/market/tickers"
resp = requests.get(url, timeout=10)
print("Status code:", resp.status_code)
print("Raw response:", resp.text)

try:
    data = resp.json()
    print("JSON keys:", list(data.keys()))
    if "data" in data:
        for ticker in data["data"][:5]:
            print(ticker)
except Exception as e:
    print("Error:", e)