import yaml

from lib.controller import Controller
from lib.model import Model
from lib.utilities.exchange import Trader, Binance
from datetime import datetime


def read_configs_from_yaml_file(yaml_file_path):
    with open(yaml_file_path) as yaml_file:
        return yaml.load(yaml_file, Loader=yaml.FullLoader)


def setup_controller(configs, exchange_account, test=False):
    _account = configs.get('exchange').get(exchange_account)
    _exchange = Binance(_account.get('key'), _account.get('secret'), test=test)
    _trader = Trader(_exchange)
    _model = Model(configs.get('starting_parameters'))
    return Controller(_model, _trader)


def handshake_key():
    return datetime.now().strftime('%Y%m%d%H%M%S%f')


def handshake_url(key):
    return 'http://localhost:5000/handshake?k={}'.format(key)
