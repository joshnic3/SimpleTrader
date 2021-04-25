import time
from datetime import datetime


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
        self.model = model
        self.trader = trader
        self.running = False
        self.runs = []
        self.errors = []

    def _execute(self, run_type):
        run = {'time': datetime.utcnow(), 'run_type': run_type.upper(), 'order': None, 'error': None}
        if self.model.evaluate_strategy() and self.model.within_limits():
            run['order'] = self.trader.market_order(
                self.model.params.get('ticker'),
                self.model.values.get('side'),
                self.model.params.get('units_to_trade')
            )
            if run['order'] is None:
                run['error'] = 'Failed to place order!'
                self.errors.append('Failed to place order!')
        self.runs.append(run)

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
        print('RUN ONCE')

    def run(self):
        self.running = True
        print('RUNNING')

    def stop(self):
        self.running = False
        print('STOPPED')

    def return_static_model(self):
        return self.model






