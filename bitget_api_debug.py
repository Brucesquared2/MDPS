import requests

url = "https://api.bitget.com/api/mix/v1/market/tickers?productType=USDT-FUTURES"
resp = requests.get(url, timeout=10)
print("Status code:", resp.status_code)
print("Raw text response:", resp.text)

try:
    data = resp.json()
    print("JSON response:", data)
except Exception as e:
    print("Failed to parse JSON:", e)