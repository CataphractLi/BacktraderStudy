from __future__ import (absolute_import, division, print_function, unicode_literals)
import backtrader as bt
import backtrader.indicators as btind
import numpy as np

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
        self.lines.VMA = btind.SMA(self.lines.Price, period=self.p.N)
        self.lines.Buy = bt.And(self.lines.Price > self.lines.VMA, self.lines.Price(-1) < self.lines.VMA(-1))
        self.lines.Sell = bt.And(self.lines.Price > self.lines.VMA, self.lines.Price(-1) < self.lines.VMA(-1))
        super(VMA, self).__init__()


class BIAS(bt.Indicator):
    
    # N=6，12，24
    # BIAS(N)=(CLOSE-MA(CLOSE,N))/MA(CLOSE,N)*100

    lines = ('BIASS', 'BIASM', 'BIASL', 'Buy', 'Sell', )

    params = (('N', (6, 12, 24)), )

    def __init__(self):
        self.lines.BIASS = (self.data.close - btind.SMA(self.data.close, period=self.p.N[0])) / \
                           btind.SMA(self.data.close, period=self.p.N[0]) * 100
        self.lines.BIASM = (self.data.close - btind.SMA(self.data.close, period=self.p.N[1])) / \
                           btind.SMA(self.data.close, period=self.p.N[1]) * 100
        self.lines.BIASL = (self.data.close - btind.SMA(self.data.close, period=self.p.N[2])) / \
                           btind.SMA(self.data.close, period=self.p.N[2]) * 100
        self.lines.Buy = bt.And(self.lines.BIASS > 5, self.lines.BIASM > 7, self.lines.BIASL > 11)
        self.lines.Sell = bt.And(self.lines.BIASS < -5, self.lines.BIASM < -7, self.lines.BIASL < -11)
        super(BIAS, self).__init__()


class TMA(bt.Indicator):

    # N=20
    # CLOSE_MA=MA(CLOSE,N)
    # TMA=MA(CLOSE_MA,N)

    lines = ('TMA', 'Buy', 'Sell', )

    params = (('N', 20), )

    def __init__(self):
        close_ma = btind.SMA(self.data.close, period=self.p.N)
        self.lines.TMA = btind.SMA(close_ma, period=self.p.N)
        self.lines.Buy = bt.And(self.data.close > self.lines.TMA, 
                                self.data.close(-1) < self.lines.TMA(-1))
        self.lines.Sell = bt.And(self.data.close < self.lines.TMA, 
                                self.data.close(-1) > self.lines.TMA(-1))
        super(TMA, self).__init__()


class TYP(bt.Indicator):

    # N1=10
    # N2=30
    # TYP=(CLOSE+HIGH+LOW)/3
    # TYPMA1=EMA(TYP,N1)
    # TYPMA2=EMA(TYP,N2)

    lines = ('TYPMA1', 'TYPMA2', 'Buy', 'Sell', )

    params = (('N1', 10), ('N2', 30), )

    def __init__(self):
        typ = (self.data.close + self.data.high + self.data.low) / 3
        self.lines.TYPMA1 = btind.EMA(typ, period=self.p.N1)
        self.lines.TYPMA2 = btind.EMA(typ, period=self.p.N2)
        self.lines.Buy = bt.And(self.lines.TYPMA1 > self.lines.TYPMA2, 
                                self.lines.TYPMA1(-1) < self.lines.TYPMA2(-1))
        self.lines.Sell = bt.And(self.lines.TYPMA1 < self.lines.TYPMA2, 
                                 self.lines.TYPMA1(-1) > self.lines.TYPMA2(-1))
        super(TYP, self).__init__()


class WMA_BS(bt.Indicator):
    
    # N=20
    # WMA=(N*CLOSE+(N-1)*REF(CLOSE,1)+...+1*REF(CLOSE,N-1))/(1+2+...+N)

    lines = ('WMABS', 'Buy', 'Sell', )

    params = (('N', 10), )

    def __init__(self):
        self.lines.WMABS = btind.WeightedMovingAverage(self.data.close, period=self.p.N)
        self.lines.Buy = bt.And(self.data.close > self.lines.WMABS, 
                                self.data.close(-1) < self.lines.WMABS(-1))
        self.lines.Sell = bt.And(self.data.close < self.lines.WMABS, 
                                 self.data.close(-1) > self.lines.WMABS(-1))
        super(WMA_BS, self).__init__()


class PAC(bt.Indicator):

    #N1=20
    #N2=20
    #UPPER=SMA(HIGH,N1,1)
    #LOWER=SMA(LOW,N2,1)

    lines = ('Upper', 'Lower', 'Buy', 'Sell', )

    params = (('N1', 20), ('N2', 20), )

    def __init__(self):
        self.addminperiod(2)
        super(PAC, self).__init__()

    def prenext(self):
        self.lines.Upper[-1] = self.data.high[0]
        self.lines.Lower[-1] = self.data.low[0]
        self.lines.Buy[-1] = False
        self.lines.Sell[-1] = False
        self.next()

    def next(self):
        self.lines.Upper[0] = 1 / self.p.N1 * self.data.high[0] + (self.p.N1 - 1) / self.p.N1 * self.lines.Upper[-1]
        self.lines.Lower[0] = 1 / self.p.N2 * self.data.low[0] + (self.p.N2 - 1) / self.p.N2 * self.lines.Lower[-1]
        self.lines.Buy[0] = self.data.close[0] > self.lines.Upper[0] and self.data.close[-1] < self.lines.Upper[-1]
        self.lines.Sell[0] = self.data.close[0] < self.lines.Lower[0] and self.data.close[-1] > self.lines.Lower[-1]


class MTM(bt.Indicator):

    # N=60
    # MTM=CLOSE-REF(CLOSE,N)

    lines = ('MTM', 'Buy', 'Close', )

    params = (('N', 60), )

    def __init__(self):
        self.lines.MTM = self.data.close - self.data.close(-self.p.N)
        self.lines.Buy = bt.And(self.lines.MTM > 0, self.lines.MTM(-1) < 0)
        self.lines.Sell = bt.And(self.lines.MTM < 0, self.lines.MTM(-1) > 0)
        super(MTM, self).__init__()


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
        self.stochastics = (self.data.close - low_n) / (high_n - low_n) * 100
        super(KDJ, self).__init__()


    def nextstart(self):
        self.lines.K[-1] = self.stochastics[0]
        self.lines.D[-1] = self.stochastics[0]
        self.lines.Buy[-1] = False
        self.lines.Sell[-1] = False
        self.next()


    def next(self):
        self.lines.K[0] = self.stochastics[0] / 3 + self.lines.K[-1] * 2 / 3
        self.lines.D[0] = self.lines.K[0] / 3 + self.lines.D[-1] * 2 / 3
        self.lines.Buy[0] = self.lines.D[0] < 20 and self.lines.K[0] > self.lines.D[0] and self.lines.K[-1] < self.lines.D[-1]
        self.lines.Sell[0] = self.lines.D[0] > 80 and self.lines.K[0] < self.lines.D[0] and self.lines.K[-1] > self.lines.D[-1]


class RMI(bt.Indicator):
    
    #N=7
    #RMI=SMA(MAX(CLOSE-REF(CLOSE,4),0),N,1)/SMA(ABS(CLOSE-REF(CLOSE,1)),N,1)*100

    lines = ('num', 'dnm', 'RMI', 'Buy', 'Sell', )

    params = (('N', 7), )


    def __init__(self):
        super(RMI, self).__init__()


    def nextstart(self):
        self.lines.num[-1] = max(self.data.close[0] - self.data.close[-4],0)
        self.lines.dnm[-1] = abs(self.data.close[0] - self.data.close[-1])
        self.lines.RMI[-1] = self.lines.num[0] / self.lines.dnm[0] * 100 
        self.lines.Buy[-1] = False
        self.lines.Sell[-1] = False
        self.next()


    def next(self):
        self.lines.num[0] = max(self.data.close[0] - self.data.close[-4], 0) * 1 / self.p.N + \
                            self.lines.num[-1] * (self.p.N-1) / self.p.N
        self.lines.dnm[0] = abs(self.data.close[0] - self.data.close[-1]) * 1 / self.p.N + \
                            self.lines.dnm[-1] * (self.p.N-1) / self.p.N
        self.lines.RMI[0] = self.lines.num[0] / self.lines.dnm[0] * 100
        self.lines.Buy[0] = self.lines.RMI[0] > 65 and self.lines.RMI[-1] < 65
        self.lines.Sell[0] = self.lines.RMI[0] < 35 and self.lines.RMI[-1] > 35


class SKDJ(bt.Indicator):

    #N=60
    #RSV=(CLOSE-MIN(LOW,N))/(MAX(HIGH,N)-MIN(LOW,N))*100
    #MARSV=SMA(RSV,3,1)
    #K=SMA(MARSV,3,1)
    #D=MA(K,3)

    lines = ('RSV', 'MARSV', 'K', 'D', 'Buy', 'Sell', )

    params = (('N', 60), )

    def __init__(self):
        self.lines.RSV = (self.data.close - btind.Lowest(self.data.low, period=self.p.N)) / \
                         (btind.Highest(self.data.high, period=self.p.N)-btind.Lowest(self.data.low, period=self.p.N)) * 100
        super(SKDJ, self).__init__()
    
    def nextstart(self):
        self.lines.MARSV[-1] = self.lines.RSV[0]
        self.lines.K[-1] = self.lines.MARSV[-1]
        self.lines.D[-1] = self.lines.MARSV[-1]
        self.lines.Buy[-1] = False
        self.lines.Sell[-1] = False
        self.next()

    def next(self):
        self.lines.MARSV[0] = self.lines.RSV[0] / 3  + self.lines.MARSV[-1] * 2 / 3
        self.lines.K[0] = self.lines.MARSV[0] / 3 + self.lines.K[-1] * 2 / 3
        self.lines.D[0] = (self.lines.K[0] + self.lines.K[-1] + self.lines.K[-2]) / 3
        self.lines.Buy[0] = self.lines.D[0] < 40 and self.lines.K[0] > self.lines.D[0] and self.lines.K[-1] < self.lines.D[-1]
        self.lines.Sell[0] = self.lines.D[0] > 60 and self.lines.K[0] < self.lines.D[0] and self.lines.K[-1] > self.lines.D[-1]


class CCI(bt.Indicator):

    #N=14
    #TP=(HIGH+LOW+CLOSE)/3
    #MA=MA(TP,N)
    #MD=MA(ABS(TP-MA),N)
    #CCI=(TP-MA)/(0.015MD)

    lines = ('CCI', 'Buy', 'Sell', )

    params = (('N', 14), )

    def __init__(self):
        tp = (self.data.high + self.data.low + self.data.close) / 3
        ma = btind.SMA(tp, period=self.p.N)
        md = btind.SMA(bt.If(tp - ma >= 0, tp - ma, ma - tp), period=self.p.N)
        self.lines.CCI = (tp-ma) / (0.015 * md)
        self.lines.Buy = bt.And(self.lines.CCI < -100, self.lines.CCI(-1) > -100)
        self.lines.Sell = bt.And(self.lines.CCI > 100, self.lines.CCI(-1) < 100)


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
        emap = btind.EMA(self.data.volume, period=self.p.N)
        self.lines.SROCVOL = (emap - emap(-self.p.M)) / emap(-self.p.M)
        self.lines.Buy = bt.And(self.lines.SROCVOL > 0, self.lines.SROCVOL(-1) < 0)
        self.lines.Sell = bt.And(self.lines.SROCVOL < 0, self.lines.SROCVOL(-1) > 0)
        super(SROCVOL, self).__init__()