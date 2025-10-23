import time
from bitget_client import BitgetClient
from strategy import Strategy
from pybitget.stream import SubscribeReq
from pybitget.enums import *

def on_ws_message(msg):
    print("WS message:", msg)
    strat.on_message(msg)

def run():
    client = BitgetClient()
    global strat
    strat = Strategy(client)

    channels = [
        SubscribeReq("mc", "ticker", "BTCUSDT"),
    ]
    client.start_ws(channels, on_ws_message)

    try:
        while True:
            balance = client.get_spot_balance()
            print("Account Balance:", balance)
            time.sleep(10)
    except KeyboardInterrupt:
        client.stop_ws()

if __name__ == "__main__":
    run()