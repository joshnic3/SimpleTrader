from statistics import mean, stdev
from datetime import datetime
from logging import getLogger

BUY = 'buy'
SELL = 'sell'


def gradient(x1, y1, x2, y2):
    if (x2 - x1) == 0:
        return 0
    return (y2 - y1) / (x2 - x1)


def trajectory(values):
    gradients = []
    x = list(range(len(values)))
    for i in range(len(values)-1):
        i += 1
        gradients.append(gradient(values[i], x[i], values[i - 1], x[i - 1]))
    return mean(gradients)/(max(gradients)-min(gradients))


class Model:

    def __init__(self, starting_parameters):
        self._log = getLogger('model')
        self.series = {}
        self.params = starting_parameters
        self.values = {}

    def update(self, ticks, capital, last_trade_value, last_side):
        self.series['times'] = [t[0] for t in ticks]
        self.series['ticks'] = [t[1] for t in ticks]

        self.values['std_dev'] = stdev(self.series['ticks'])

        self.series['rolling_mean'] = [mean(self.series.get('ticks')[:i]) if i > 0 else v for i,  v in enumerate(self.series.get('ticks'))]
        self.series['sell_limits'] = [m + self.values.get('std_dev') * self.params.get('sell_appetite') for m in self.series.get('rolling_mean')]
        self.series['buy_limits'] = [m - self.values.get('std_dev') * self.params.get('buy_appetite') for m in self.series.get('rolling_mean')]

        self.values['sell_limit'] = self.series.get('sell_limits')[-1]
        self.values['buy_limit'] = self.series.get('buy_limits')[-1]
        self.values['rolling_mean'] = self.series.get('rolling_mean')[-1]
        self.values['current_value'] = self.series.get('ticks')[-1]

        self.values['capital'] = capital
        self.values['last_trade_value'] = last_trade_value
        self.values['side'] = SELL if last_side.lower() == BUY else BUY
        self.values['trajectory'] = trajectory(self.series['ticks'])
        self.values['current_trade_value'] = self.values.get('current_value') * self.params.get('units_to_trade')
        self.values['last_update'] = datetime.utcnow()

    def evaluate_strategy(self):
        if self.values['side'] == BUY:
            buy = self.values.get('current_value') < self.values.get('buy_limit')
            self._log.info('strategy, buy: {}'.format(str(buy)))
            return buy
        elif self.values['side'] == SELL:
            sell = self.values.get('current_value') > self.values.get('sell_limit')
            self._log.info('strategy, sell: {}'.format(str(sell)))
            return sell
        else:
            return False

    def within_limits(self):
        # Value trajectory(gradient) needs to be positive over this run period.
        if self.values.get('trajectory') < self.params.get('trajectory_limit'):
            self._log.info('limits, trajectory < trajectory_limit')
            return False

        # Cost of trade cannot be more then our available capital.
        if self.values.get('current_trade_value') > self.values.get('capital'):
            self._log.info('limits, current_trade_value > capital')
            return False

        # If we got here all is good.
        return True

    def as_dict(self):
        return {
            'params': self.params,
            'values': self.values,
            'series': self.series
        }
