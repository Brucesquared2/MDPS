"""Simple placeholder Vortex indicator module.
Replace the implementation with your production Vortex code.
"""

def vortex_run(params: dict) -> dict:
    """Run the Vortex indicator logic.

    params example: {"symbol": "BTCUSDT", "window": 14}
    Returns a JSON-serializable dict with signals and metrics.
    """
    symbol = params.get("symbol", "UNKNOWN")
    window = int(params.get("window", 14))

    # placeholder computation
    signals = [{"timestamp": 0, "signal": "hold"}]
    metrics = {"window": window, "symbol": symbol}

    return {"job": "vortex", "symbol": symbol, "signals": signals, "metrics": metrics}
