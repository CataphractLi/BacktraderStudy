from __future__ import (absolute_import, division, print_function, unicode_literals)
import backtrader as bt
import backtrader.indicators as btind

# 价格动量类指标
## 可直接引用指标: PriceOscillator

class ER(bt.Indicator):

    # BullPower=HIGH-EMA(CLOSE,N)
    # BearPower=LOW-EMA(CLOSE,N)

    lines = ('BullPower', 'BearPower', 'Buy', 'Sell', )

    params = (('N', 20),)

    def __init__(self):
        self.lines.BullPower = self.data.high - btind.EMA(self.data.close, period=self.p.N)
        self.lines.BearPower = self.data.low - btind.EMA(self.data.close, period=self.p.N)
        self.lines.Buy = bt.And(self.lines.BearPower > 0, self.lines.BearPower(-1) < 0)
        self.lines.Sell = bt.And(self.lines.BullPower < 0, self.lines.BullPower(-1) > 0)
        super(ER, self).__init__()


class DPO(bt.Indicator):

    # DPO=CLOSE-REF(MA(CLOSE,N),N/2+1)

    lines = ('DPO', 'Buy', 'Sell', )

    params = (('N', 20),)

    def __init__(self):
        self.lines.DPO = self.data.close - btind.SMA(self.data.close, period=self.p.N)(-(self.p.N // 2 + 1))
        self.lines.Buy = bt.And(self.lines.DPO > 0, self.lines.DPO(-1) < 0)
        self.lines.Sell = bt.And(self.lines.DPO < 0, self.lines.DPO(-1) > 0)
        super(DPO, self).__init__()


class POS(bt.Indicator):

    #PRICE=(CLOSE-REF(CLOSE,N))/REF(CLOSE,N)
    #POS=(PRICE-MIN(PRICE,N))/(MAX(PRICE,N)-MIN(PRICE,N))

    lines = ('POS', 'Buy', 'Sell', )

    params = (('N', 100),)

        #self.POS_buy = bt.And(self.POS.lines.POS > 80, self.POS.lines.POS(-1) < 80)
        #self.POS_sell = bt.And(self.POS.lines.POS < 20, self.POS.lines.POS(-1) > 20)

    def __init__(self):
        price = (self.data.close - self.data.close(-self.p.N)) / self.data.close(-self.p.N)
        self.lines.POS = (price - btind.Lowest(price, period=self.p.N)) / (btind.Highest(price, period=self.p.N) - btind.Lowest(price, period=self.p.N)) * 100
        self.lines.Buy = bt.And(self.lines.POS > 80, self.lines.POS(-1) < 80)
        self.lines.Sell = bt.And(self.lines.POS < 20, self.lines.POS(-1) > 20)
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

    lines = ('TII', 'TII_Signal', 'Buy', 'Sell', )

    params = (('N1', 40), ('N2', 9), )
        
        #self.TII_buy = bt.And(self.TII.lines.TII > self.TII.lines.TII_Signal, 
        #                      self.TII.lines.TII(-1) < self.TII.lines.TII_Signal(-1))
        #self.TII_sell = bt.And(self.TII.lines.TII < self.TII.lines.TII_Signal, 
        #                       self.TII.lines.TII(-1) > self.TII.lines.TII_Signal(-1))

    def __init__(self):
        M = self.p.N1 // 2 + 1
        close_ma = btind.SMA(self.data.close, period=self.p.N1)
        dev = self.data.close - close_ma
        devpos = bt.If(dev > 0, dev, 0)
        devneg = bt.If(dev < 0, -dev, 0)
        sumpos = btind.SumN(devpos, period=M)
        sumneg = btind.SumN(devneg, period=M)
        self.lines.TII = 100 * sumpos / (sumpos + sumneg)
        self.lines.TII_Signal = btind.EMA(self.lines.TII, period=self.p.N2)
        self.lines.Buy = bt.And(self.lines.TII > self.lines.TII_Signal, 
                                self.lines.TII(-1) < self.lines.TII_Signal(-1))
        self.lines.Sell = bt.And(self.lines.TII < self.lines.TII_Signal, 
                                 self.lines.TII(-1) > self.lines.TII_Signal(-1))
        super(TII, self).__init__()


class ADTM(bt.Indicator):
    
    #N=20
    #DTM=IF(OPEN>REF(OPEN,1),MAX(HIGH-OPEN,OPEN-REF(OPEN,1)),0)
    #DBM=IF(OPEN<REF(OPEN,1),MAX(OPEN-LOW,REF(OPEN,1)-OPEN),0)
    #STM=SUM(DTM,N)
    #SBM=SUM(DBM,N)
    #ADTM=(STM-SBM)/MAX(STM,SBM)

    lines = ('ADTM', 'Buy', 'Sell', )
    
    params = (('N', 20), )

    def __init__(self):
        DTM = bt.If(self.data.open > self.data.open(-1), 
                    bt.Max(self.data.high-self.data.open, self.data.open-self.data.open(-1)), 
                    0)
        DBM = bt.If(self.data.open < self.data.open(-1), 
                    bt.Max(self.data.open-self.data.low, self.data.open(-1)-self.data.open), 
                    0)
        STM = btind.SumN(DTM, period=self.p.N)
        SBM = btind.SumN(DBM, period=self.p.N)
        self.lines.ADTM = (STM-SBM)/bt.Max(STM, SBM)
        self.lines.Buy = bt.And(self.lines.ADTM > 0.5,
                                self.lines.ADTM(-1) < 0.5)
        self.lines.Sell = bt.And(self.lines.ADTM < -0.5,
                                 self.lines.ADTM(-1) > -0.5)
        super(ADTM, self).__init__()


class MADisplaced(bt.Indicator):

    #N=20
    #M=10
    #MA_CLOSE=MA(CLOSE,N)
    #MADisplaced=REF(MA_CLOSE,M)

    lines = ('MADisplaced', 'Buy', 'Sell', )

    params = (('N', 20), ('M', 10), )

    def __init__(self):
        ma_close = btind.SMA(self.data.close, period=self.p.N)
        self.lines.MADisplaced = ma_close(-self.p.M)
        self.lines.Buy = bt.And(self.data.close > self.lines.MADisplaced, 
                                self.data.close(-1) < self.lines.MADisplaced(-1))
        self.lines.Sell = bt.And(self.data.close < self.lines.MADisplaced, 
                                 self.data.close(-1) > self.lines.MADisplaced(-1))
        super(MADisplaced, self).__init__()


class T3(bt.Indicator):
    
    #N=20
    #VA=0.5
    #T1=EMA(CLOSE,N)*(1+VA)-EMA(EMA(CLOSE,N),N)*VA
    #T2=EMA(T1,N)*(1+VA)-EMA(EMA(T1,N),N)*VA
    #T3=EMA(T2,N)*(1+VA)-EMA(EMA(T2,N),N)*VA

    lines = ('T3', 'Buy', 'Sell', )

    params = (('N', 20), ('VA', 0.5), )

    def __init__(self):
        t1 = btind.EMA(self.data.close, period=self.p.N) * (1 + self.p.VA) - \
             btind.EMA(btind.EMA(self.data.close, period=self.p.N), period=self.p.N) * self.p.VA
        t2 = btind.EMA(t1, period=self.p.N) * (1 + self.p.VA) - \
             btind.EMA(btind.EMA(t1, period=self.p.N), period=self.p.N) * self.p.VA
        self.lines.T3 = btind.EMA(t2, period=self.p.N) * (1 + self.p.VA) - \
                        btind.EMA(btind.EMA(t2, period=self.p.N), period=self.p.N) * self.p.VA
        self.lines.Buy = bt.And(self.data.close > self.lines.T3, self.data.close(-1) > self.lines.T3(-1))
        self.lines.Sell = bt.And(self.data.close < self.lines.T3, self.data.close(-1) < self.lines.T3(-1))
        super(T3, self).__init__()


class VMA(bt.Indicator):

    #N=20
    #PRICE=(HIGH+LOW+OPEN+CLOSE)/4
    #VMA=MA(PRICE,N)

    lines = ('Price', 'VMA', 'Buy', 'Sell', )

    params = (('N', 20), )

    def __init__(self):
        self.lines.Price = (self.data.high + self.data.low + self.data.open + self.data.close) / 4
        self.lines.VMA = self.SMA(self.lines.Price, period=self.p.N)
        self.lines.Buy = bt.And(self.lines.Price > self.lines.VMA, self.lines.Price(-1) < self.lines.VMA(-1))
        self.lines.Sell = bt.And(self.lines.Price > self.lines.VMA, self.lines.Price(-1) < self.lines.VMA(-1))
        super(VMA, self).__init__()


# 价格翻转类指标

class KDJ(bt.Indicator):
    
    #N=40
    #LOW_N=MIN(LOW,N)
    #HIGH_N=MAX(HIGH,N)
    #Stochastics=(CLOSE-LOW_N)/(HIGH_N-LOW_N)*100
    #K=SMA(Stochastics,3,1)
    #D=SMA(K,3,1)

    lines = ('K', 'D', 'Buy', 'Sell', )
    
    params = (('N', 40), )

    def __init__(self):
        low_n = btind.Lowest(self.data.low, period=self.p.N)
        high_n = btind.Highest(self.data.high, period=self.p.N)
        stochastics = (self.data.close - low_n) / (high_n - low_n) * 100
        self.lines.K = stochastics / 3 + stochastics(-1) * 2 / 3
        self.lines.D = self.lines.K / 3 + self.lines.K(-1) * 2 / 3
        self.lines.Buy = bt.And(self.lines.D < 20, 
                                self.lines.K > self.lines.D, 
                                self.lines.K(-1) < self.lines.D(-1))
        self.lines.Sell = bt.And(self.lines.D > 80, 
                                 self.lines.K < self.lines.D, 
                                 self.lines.K(-1) > self.lines.D(-1))
        super(KDJ, self).__init__()


# 成交量指标

class MAAMT(bt.Indicator):
    
    #N=40
    #MAAMT=MA(AMOUNT,N)

    lines = ('MAAMT', 'Buy', 'Sell', )

    params = (('N', 40), )

    def __init__(self):
        self.lines.MAAMT = btind.SMA(self.data.volume, period=self.p.N)
        self.lines.Buy = bt.And(self.data.volume > self.lines.MAAMT, 
                                self.data.volume(-1) < self.lines.MAAMT(-1))
        self.lines.Sell = bt.And(self.data.volume < self.lines.MAAMT, 
                                self.data.volume(-1) > self.lines.MAAMT(-1))
        super(MAAMT, self).__init__()


class SROCVOL(bt.Indicator):

    #N=20
    #M=10
    #EMAP=EMA(VOLUME,N)
    #SROCVOL=(EMAP-REF(EMAP,M))/REF(EMAP,M)

    lines = ('SROCVOL', 'Buy', 'Sell', )

    params = (('N', 20), ('M', 10), )

    def __init__(self):
        emap = btind.EMA(self.data.volume, self.p.N)
        self.lines.SROCVOL = (emap - emap(-self.p.M)) / emap(-self.p.M)
        self.lines.Buy = bt.And(self.lines.SROCVOL > 0, self.lines.SROCVOL(-1) < 0)
        self.lines.Sell = bt.And(self.lines.SROCVOL < 0, self.lines.SROCVOL(-1) > 0)
        super(SROCVOL, self).__init__()