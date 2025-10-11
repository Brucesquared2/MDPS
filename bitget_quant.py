import ccxt

exchange = ccxt.bitget({
    'apiKey': 'YOUR_API_KEY',
    'secret': 'YOUR_API_SECRET',
    'password': 'YOUR_API_PASSPHRASE',  # Bitget calls this "passphrase"
})

# Test connection: Fetch account balance
try:
    balance = exchange.fetch_balance()
    print(balance)
except Exception as e:
    print("Error connecting to Bitget:", e)