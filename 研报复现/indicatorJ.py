from __future__ import (absolute_import, division, print_function, unicode_literals)
import backtrader as bt
import backtrader.indicators as btind

# 价格动量类因子

class ER(bt.Indicator):

    # BullPower=HIGH-EMA(CLOSE,N)
    # BearPower=LOW-EMA(CLOSE,N)

    lines = ('BullPower', 'BearPower',)

    params = (('N', 20),)

    def __init__(self):
        self.lines.BullPower = self.data.high - btind.EMA(self.data.close, period=self.p.N)
        self.lines.BearPower = self.data.low - btind.EMA(self.data.close, period=self.p.N)
        super(ER, self).__init__()


class DPO(bt.Indicator):

    # DPO=CLOSE-REF(MA(CLOSE,N),N/2+1)

    lines = ('DPO', )

    params = (('N', 20),)

    def __init__(self):
        self.lines.DPO = self.data.close - btind.SMA(self.data.close, period=self.p.N)(-(self.p.N // 2 + 1))
        super(DPO, self).__init__()


class POS(bt.Indicator):

    #PRICE=(CLOSE-REF(CLOSE,N))/REF(CLOSE,N)
    #POS=(PRICE-MIN(PRICE,N))/(MAX(PRICE,N)-MIN(PRICE,N))

    lines = ('POS', )

    params = (('N', 100),)

    def __init__(self):
        price = (self.data.close - self.data.close(-self.p.N)) / self.data.close(-self.p.N)
        self.lines.POS = (price - btind.Lowest(price, period=self.p.N)) / (btind.Highest(price, period=self.p.N) - btind.Lowest(price, period=self.p.N)) * 100
        super(POS, self).__init__()


class TII(bt.Indicator):
    
    #N1=40
    #M=[N1/2]+1
    #N2=9
    #CLOSE_MA=MA(CLOSE,N1)
    #DEV=CLOSE-CLOSE_MA
    #DEVPOS=IF(DEV>0,DEV,0)
    #DEVNEG=IF(DEV<0,-DEV,0)
    #SUMPOS=SUM(DEVPOS,M)
    #SUMNEG=SUM(DEVNEG,M)
    #TII=100*SUMPOS/(SUMPOS+SUMNEG)
    #TII_SIGNAL=EMA(TII,N2)

    lines = ('TII', 'TII_Signal', )

    params = (('N1', 40), ('N2', 9), )

    def __init__(self):
        M = self.p.N1 // 2 + 1
        close_ma = btind.SMA(self.data.close, period=self.p.N1)
        dev = self.data.close - close_ma
        devpos = bt.If(dev > 0, dev, 0)
        devneg = bt.If(dev < 0, -dev, 0)
        sumpos = btind.SumN(devpos, M)
        sumneg = btind.SumN(devneg, M)
        self.lines.TII = 100 * sumpos / (sumpos + sumneg)
        self.lines.TII_Signal = btind.EMA(self.lines.TII, period=self.p.N2)
        super(TII, self).__init__()


class ADTM(bt.Indicator):
    #N=20
    #DTM=IF(OPEN>REF(OPEN,1),MAX(HIGH-OPEN,OPEN-REF(OPEN,1)),0)
    #DBM=IF(OPEN<REF(OPEN,1),MAX(OPEN-LOW,REF(OPEN,1)-OPEN),0)
    #STM=SUM(DTM,N)
    #SBM=SUM(DBM,N)
    #ADTM=(STM-SBM)/MAX(STM,SBM)

    lines = ('ADTM', )
    
    params = (('N', 20), )

    def __init__(self):
        DTM = bt.If(self.data.open > self.data.open(-1), 
                    bt.Max(self.data.high-self.data.open, self.data.open-self.data.open(-1)), 
                    0)
        DBM = bt.If(self.data.open < self.data.open(-1), 
                    bt.Max(self.data.open-self.data.low, self.data.open(-1)-self.data.open), 
                    0)
        STM = btind.SumN(DTM, self.p.N)
        SBM = btind.SumN(DBM, self.p.N)
        self.lines.ADTM = (STM-SBM)/bt.Max(STM, SBM)
        super(ADTM, self).__init__()

