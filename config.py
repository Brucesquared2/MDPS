import os

# Load Bitget credentials from environment variables
API_KEY = os.getenv("BITGET_API_KEY")
API_SECRET = os.getenv("BITGET_API_SECRET") 
API_PASSPHRASE = os.getenv("BITGET_API_PASSPHRASE")

if not all([API_KEY, API_SECRET, API_PASSPHRASE]):
    raise ValueError(
        "Missing Bitget API credentials. Set environment variables:\n"
        "BITGET_API_KEY, BITGET_API_SECRET, BITGET_API_PASSPHRASE"
    )
