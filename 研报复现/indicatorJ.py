from __future__ import (absolute_import, division, print_function, unicode_literals)
import backtrader as bt
import backtrader.indicators as btind

class ER(bt.Indicator):

    # BullPower=HIGH-EMA(CLOSE,N)
    # BearPower=LOW-EMA(CLOSE,N)

    lines = ('BullPower', 'BearPower',)

    params = (('ER_n', 20),)

    def __init__(self):
        self.lines.BullPower = self.data.high - btind.ExponentialMovingAverage(self.data.close, self.params.ER_n)
        self.lines.BearPower = self.data.low - btind.ExponentialMovingAverage(self.data.close, self.params.ER_n)
        super(ER, self).__init__()