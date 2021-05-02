from argparse import ArgumentParser
from datetime import datetime

import yaml

from lib.controller import Controller
from lib.model import Model
from lib.utilities.exchange import Trader, Binance


def read_cmdline_args():
    parser = ArgumentParser()
    parser.add_argument('-c', '--configs', required=True, help="YAML configuration file path.")
    parser.add_argument('-a', '--account', required=True, help="Exchange account.")
    parser.add_argument('-b', '--browser', default=False, action='store_true', help="Opens client in browser on start.")
    parser.add_argument('-d', '--debug', default=False, action='store_true', help="Debug mode.")
    parser.add_argument('-t', '--test_exchange', default=False, action='store_true', help="Runs against test exchange API.")
    return parser.parse_args()


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
