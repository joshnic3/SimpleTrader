from statistics import mean, stdev
from datetime import datetime

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
        self.time_series = []
        self.series = {}
        self.params = starting_parameters
        self.values = {
            'side': self.params.get('starting_side')
        }

    def switch_side(self, last_side=None):
        side = last_side if last_side is not None else self.values.get('side')
        self.values['side'] = BUY if side == SELL else SELL

    def update(self, ticks, capital, last_trade_value, last_side):
        self.series['times'] = [t[0] for t in ticks]
        self.series['values'] = [t[1] for t in ticks]
        self.values['last_update'] = datetime.utcnow()
        self.values['trajectory'] = trajectory(self.series['values'])
        self.values['current_value'] = self.series['values'][-1]
        self.values['rolling_mean'] = mean(self.series['values'])
        self.values['std_dev'] = stdev(self.series['values'])
        self.values['capital'] = capital
        self.series['sell_limits'] = [self.values.get('rolling_mean') + self.values.get('std_dev') * self.params.get('sell_appetite') for v in self.series.get('values')]
        self.series['buy_limits'] = [self.values.get('rolling_mean') - self.values.get('std_dev') * self.params.get('buy_appetite') for v in self.series.get('values')]
        self.values['sell_limit'] = self.series.get('sell_limits')[-1]
        self.values['buy_limit'] = self.series.get('buy_limits')[-1]
        self.values['last_trade_value'] = last_trade_value
        self.values['side'] = SELL if last_side == BUY else BUY
        self.values['current_trade_value'] = self.values.get('current_value') * self.params.get('units_to_trade')

    def evaluate_strategy(self):
        if self.values['side'] == SELL:
            if self.values['last_trade_value'] > self.values.get('current_trade_value'):
                return False

        if self.values['side'] == BUY:
            if self.values['last_trade_value'] < self.values.get('current_trade_value'):
                return False

        if self.values['side'] == BUY:
            return self.values.get('current_value') < self.values.get('buy_limit')
        elif self.values['side'] == SELL:
            return self.values.get('current_value') > self.values.get('sell_limit')
        else:
            return False

    def within_limits(self):
        # Value trajectory(gradient) needs to be positive over this run period.
        if self.values['trajectory'] < self.params.get('trajectory_limit'):
            return False

        # Cost of trade cannot be more then our available capital.
        if self.values.get('current_value') * self.params.get('units_to_trade') > self.values.get('capital'):
            return False

        # If we got here all is good.
        return True

    def as_dict(self):
        return {
            'time_series': self.time_series,
            'params': self.params,
            'values': self.values,
            'series': self.series
        }
