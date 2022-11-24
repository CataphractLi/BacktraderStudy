# Concepts

## Operating the platform

### Line Iterators

Backtrader采用和Python中`Iterator`类似的概念来运行整个策略，而迭代的关键方法有如下几种：

+ `next`方法：在达到minimum period后每次迭代都会运行。与该Line Iterator相关的`datas`也会移到下一个索引处。
+ `prenext`方法：在到达minimum period之前每次迭代都会运行。
+ `nextstart`方法：只会在到达minimum period时运行一次，一般来说会内置在最后运行一次`next`方法。

#### Extra methods for Indicators

指标额外支持批处理模式（不必要），用来加快运算。额外的方法有：

+ `once(self, start, end)`方法：在到达minimum period后每次迭代都会运行。
+ `preonce(self, start, end)`
+ `oncestart(self, start, end)`

#### Minimum Period

以下面的均线指标为例：

```
class SimpleMovingAverage(Indicator):
    lines = ('sma',)
    params = dict(period=20)

    def __init__(self):
        ...  # Not relevant for the explanation

    def prenext(self):
        print('prenext:: current period:', len(self))

    def nextstart(self):
        print('nextstart:: current period:', len(self))
        # emulate default behavior ... call next
        self.next()

    def next(self):
        print('next:: current period:', len(self))

sma = btind.SimpleMovingAverage(self.data, period=25)
```

在这个例子中，假设`self.data`的周期为1，且无延迟，则`period=25`的情况下：

+ `prenext`会执行24次
+ `nextstart`会执行一次(在第一次满足minimum period)的情况下
+ `next`会执行n次，直到数据全部被运行完

再看下面这个例子：
```
sma1 = btind.SimpleMovingAverage(self.data, period=25)
sma2 = btind.SimpleMovingAverage(sma1, period=20)
```

`sma1`中的`prenext`, `nextstart`和`next`运行次数和上个例子相同，而`sma2`的数据来源是`sma1`，周期为20。因此：

+ `prenext`方法会运行25+18=43次 (或者24+19)。`sma1`需要运行25次迭代才能产生第一个值，而之后还需要产生18个值（总共19个），才能在下一次迭代中有足够的数据量来进入`nextstart`方法
+ `nextstart`方法和上述例子相同，只会运行一次（第44次）
+ `next`会运行n次，直到数据来源被运行完（第45次）

一般情况下，minimum period会根据数据来源自动进行调整，而只有当迭代次数超过minimum period了之后`next`方法才会启动。

*注：可以使用`setminperiod(minperiod)`来手动调整，但不推荐。*

### Up and Running

Getting up and running involves at least 3 Lines objects:

+ A Data feed
+ A Strategy (actually a class derived from Strategy)
+ A Cerebro (brain in Spanish)

### Data Feeds

一个完整的创建数据槽的代码格式如下：

```
data = btfeeds.YahooFinanceCSVData( # 数据来源 YahooFinance
    dataname=datapath,
    reversed=True, # Yahoo的数据从最新到最久，因此要倒序
    fromdate=datetime.datetime(2014, 1, 1),
    todate=datetime.datetime(2014, 12, 31), # 如果原始数据太过庞大，可以使用fromdate和todate限定时间范围
    timeframe=bt.TimeFrame.Days, # 设定时间间隔单位
    compression=1, # 压缩值
    name='Yahoo' # 数据槽名字
   )
```

### A Strategy (derived) class

一个完整的策略类包含了以下几个部分：

+ `__init__`: 用于为策略创建指标和其他的计算支持。
+ `next`: 将策略运用到每一天的数据(bar)。
+ `start`: 在回测开始的时候运行
+ `stop`: 在回测结束的时候运行
+ `notify_order`: 用于在订单成交的时候发出提醒