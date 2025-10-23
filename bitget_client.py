from pybitget import Client
from pybitget.stream import BitgetWsClient, SubscribeReq, handel_error
from pybitget.enums import *
import threading
import time
from config import API_KEY, API_SECRET, API_PASSPHRASE

class BitgetClient:
    def __init__(self):
        self.rest = Client(API_KEY, API_SECRET, passphrase=API_PASSPHRASE)
        self.ws = None
        self._stop_ws = False

    def get_spot_balance(self):
        return self.rest.spot_get_accounts()

    def place_order_spot(self, symbol, side, price, size, order_type="limit"):
        return self.rest.spot_place_order(
            symbol=symbol,
            side=side,
            price=str(price),
            size=str(size),
            orderType=order_type
        )

    def cancel_order_spot(self, symbol, order_id=None, client_oid=None):
        return self.rest.spot_cancel_order(
            symbol=symbol,
            orderId=order_id,
            clientOid=client_oid
        )

    def start_ws(self, channels, on_message):
        self.ws = (BitgetWsClient(api_key=API_KEY,
                                  api_secret=API_SECRET,
                                  passphrase=API_PASSPHRASE,
                                  verbose=False)
                   .error_listener(handel_error)
                   .build())

        self.ws.subscribe(channels, on_message)

        def run_loop():
            while not self._stop_ws:
                time.sleep(1)
            self.ws.close()

        t = threading.Thread(target=run_loop, daemon=True)
        t.start()

    def stop_ws(self):
        self._stop_ws = True