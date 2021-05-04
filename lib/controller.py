import time
from datetime import datetime

from logging import getLogger


def runner(controller, interval):
    print('running')
    while True:
        try:
            controller.update_model()
            controller.run_once(run_type='automated')
        except Exception as error:
            print(str(error))
        time.sleep(interval)


class Controller:

    def __init__(self, model, trader):
        self._log = getLogger('controller')
        self.model = model
        self.trader = trader
        self.running = False
        self.runs = []
        self.errors = []

    def _execute(self, run_type):
        run = {'time': datetime.utcnow(), 'run_type': run_type.upper(), 'trade': None, 'error': None}
        should_trade = self.model.evaluate_strategy()
        within_limits = self.model.within_limits()

        if should_trade and within_limits:
            trade = self.trader.market_order(
                self.model.params.get('ticker'),
                self.model.values.get('side'),
                self.model.params.get('units_to_trade')
            )
            if trade is None:
                run['error'] = 'Failed to trade!'
                self._log.warn('TRADE FAILED!')
                self.errors.append('Failed to place order!')
        self.runs.append(run)

        # Log execution.
        self._log.info('executed, should_trade: {}, within_limits: {}, trade'.format(
            should_trade, within_limits, run.get('trade')
        ))

    def update_model(self):
        try:
            ticks = self.trader.exchange.get_ticks(
                self.model.params.get('ticker'),
                self.model.params.get('look_back_minutes')
            )
            capital = self.trader.exchange.get_balance(
                self.model.params.get('base_currency')
            )
            last_trade_value, last_side = self.trader.get_last_order(
                self.model.params.get('ticker'),
                keys=['cummulativeQuoteQty', 'side']
            )
            self.model.update(ticks, capital, float(last_trade_value), last_side.lower())
            if self.running:
                self._execute('automated')
        except Exception as error:
            self.errors.append(str(error))

    def run_once(self):
        self._execute('manual')
        self._log.info('run once')

    def run(self):
        self.running = True
        self._log.info('running')

    def stop(self):
        self.running = False
        self._log.info('stopped')

    def return_static_model(self):
        return self.model

    def modify_parameter(self, key, new_value):
        old_value = self.model.params.get(key)
        if old_value is None:
            return None
        try:
            self.model.params[key] = type(old_value)(new_value)
            self._log.info('modified_parameter, key: {}, old: {}, new: {}'.format(key, old_value, new_value))
        except TypeError:
            return None
        except ValueError:
            return None
        return self.model.params.get(key)







