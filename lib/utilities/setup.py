from argparse import ArgumentParser
from datetime import datetime

from logging import INFO, getLogger, StreamHandler, Formatter, FileHandler


import yaml

from lib.controller import Controller
from lib.model import Model
from lib.utilities.exchange import Trader, Binance

import os
import sys


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


def configure_controller(configs, exchange_account, test=False):
    _account = configs.get('exchange').get(exchange_account)
    _exchange = Binance(_account.get('key'), _account.get('secret'), test=test)
    _trader = Trader(_exchange)
    _model = Model(configs.get('starting_parameters'))
    return Controller(_model, _trader)


def setup_logger(name, log_path, level=INFO):
    name = '{}_{}.log'.format(name, datetime.now().strftime('%Y%m%d_%H%M%S'))
    path = os.path.join(log_path, name)

    logger = getLogger()
    logger.setLevel(level)

    formatter = Formatter('%(asctime)s, %(levelname)s, %(name)s, %(message)s')

    file_handler = FileHandler("{0}_{1}.log".format(path, name))
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    logger.addHandler(file_handler)

    console_handler = StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)

    return logger


