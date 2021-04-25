import hashlib
import hmac
from datetime import datetime
from operator import itemgetter
from urllib.parse import urlencode

import requests


class BinanceError(Exception):
    pass


class Binance:

    BASE_URL = 'https://api.binance.com'
    TEST_URL = 'https://testnet.binance.vision'
    ENDPOINTS = {
        'klines': '/api/v3/klines',
        'account': '/api/v3/account',
        'orders': '/api/v3/allOrders',
        'order': '/api/v3/order'
    }
    METHODS = {
        'GET': requests.get,
        'POST': requests.post
    }

    def __init__(self, key, secret, test=False):
        self._key = key
        self._secret = secret
        self.base = self.TEST_URL if test else self.BASE_URL

    @staticmethod
    def _sign_payload(payload, secret):
        payload.update({'timestamp': int(datetime.timestamp(datetime.now()) * 1000)})
        payload.update(
            {'signature': hmac.new(secret.encode('utf-8'), urlencode(payload).encode('utf-8'),
                                   hashlib.sha256).hexdigest()}
        )
        return payload

    def send_signed_request(self, method, endpoint, payload=None, sign=False, allow=None):
        # Prepare request parameters
        method = method.upper()
        payload = payload if isinstance(payload, dict) else {}

        # Add timestamp and signature if required
        if sign:
            payload = self._sign_payload(payload, self._secret)

        # Request data
        request_function = self.METHODS.get(method)
        response = request_function(
            self.base + self.ENDPOINTS.get(endpoint),
            params=payload,
            headers={'X-MBX-APIKEY': self._key}
        )

        # Try to extract response JSON
        if response.status_code == 200:
            return response.json()
        if response.status_code == 400:
            if allow is not None and allow in response.json().get('msg'):
                return None
        raise BinanceError('Request Error: {}'.format(response.json().get('msg')))

    def get_ticks(self, symbol, look_back_minutes):
        times = []
        levels = []
        headers = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume',
                   'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
        params = {'symbol': symbol, 'interval': '1m', 'limit': look_back_minutes}
        result = self.send_signed_request('GET', 'klines', payload=params)
        open_time_index = headers.index('close_time')
        close_index = headers.index('close')
        for row in sorted(result, key=itemgetter(0)):
            times.append(datetime.fromtimestamp(row[open_time_index]/1000))
            levels.append(float(row[close_index]))
        return list(zip(times, levels))

    def get_balance(self, symbol):
        result = self.send_signed_request('GET', 'account', sign=True)
        if result:
            balances = result.get('balances')
            balance_map = {b.get('asset'): float(b.get('free')) for b in balances if float(b.get('free')) > 0}
            return balance_map.get(symbol)
        return None

    def get_orders(self, symbol, order_id=None):
        params = {'symbol': symbol}
        if order_id is not None:
            params['orderId'] = order_id
            params['limit'] = 1
        result = self.send_signed_request('GET', 'orders', payload=params, sign=True)
        if result:
            return result
        return None

    def post_market_order(self, symbol, side, units):
        params = {'symbol': symbol.upper(), 'side': side.upper(), 'type': 'MARKET', 'quantity': units}
        response = self.send_signed_request('POST', 'order', payload=params, sign=True, allow='MIN_NOTIONAL')
        if response:
            return response.get('orderId')
        return None


class Trader:

    def __init__(self, exchange):
        self.exchange = exchange
        self.orders = []

    def market_order(self, symbol, side, units):
        order_id = self.exchange.post_market_order(symbol, side, units)
        if order_id:
            order = {'time': datetime.utcnow(), 'id': order_id, 'symbol': symbol.upper(), 'status': 'new'.upper(),
                     'side': side.upper(), 'units': None, 'price': None}
            self.orders.append(order)
            return order_id
        return None

    def update_orders(self):
        for i, order in enumerate(self.orders):
            result = self.exchange.get_orders(order.get('symbol'), order_id=order.get('id'))
            if result is not None and len(result) == 1:
                order_data = result[0]
                self.orders[i]['status'] = order_data.get('status')
                self.orders[i]['units'] = order_data.get('executedQty')
                self.orders[i]['price'] = order_data.get('cummulativeQuoteQty')

    def get_last_order(self, symbol, key=None, keys=None):
        orders = self.exchange.get_orders(symbol)
        if orders:
            last_order = orders[-1]
            if key is not None:
                return last_order.get(key)
            if keys is not None:
                return [last_order.get(key) for key in keys]
            return last_order
        return None

