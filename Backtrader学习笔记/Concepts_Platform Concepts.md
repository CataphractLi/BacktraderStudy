# Concepts

## Platform concepts

### Data Feeds

#### Shortcut for data feeds

The self.datas array items can be directly accessed with additional automatic member variables:

+ `self.data` = `self.datas[0]` (单数据)
+ `self.dataX` = `self.datas[X]` （多数据）

#### Omitting the Data Feeds

在单数据情况下，Indicator中的Data Feeds参数可忽略。
```
class MyStrategy(bt.Strategy):
    params = dict(period=20)

    def __init__(self):

        sma = btind.SimpleMovingAverage(period=self.params.period)
        # 等同于 sma = btind.SimpleMovingAverage(self.data, period=self.params.period)
```
#### Almost everything is a Data Feed

可以使用`Indicator`或者`Operation`的结果来作为Data Feed进行新运算。

```
class MyStrategy(bt.Strategy):
    params = dict(period1=20, period2=25, period3=10, period4)

    def __init__(self):

        sma1 = btind.SimpleMovingAverage(self.datas[0], period=self.p.period1)

        # This 2nd Moving Average operates using sma1 as "data"
        sma2 = btind.SimpleMovingAverage(sma1, period=self.p.period2)

        # New data created via arithmetic operation
        something = sma2 - sma1 + self.data.close

        # This 3rd Moving Average operates using something  as "data"
        sma3 = btind.SimpleMovingAverage(something, period=self.p.period3)

        # Comparison operators work too ...
        greater = sma3 > sma1

        # Pointless Moving Average of True/False values but valid (无意义但可行)
        # This 4th Moving Average operates using greater  as "data"
        sma3 = btind.SimpleMovingAverage(greater, period=self.p.period4)
    ...
```

### Parameters

参数可以通过元组中的元组或者字典来表达。`params = (('period', 20),)`等同于`params= dict(period=20)`。

`self.params` = `self.p`

### Lines

```
class MyStrategy(bt.Strategy):
    params = dict(period=20)

    def __init__(self):

        self.movav = btind.SimpleMovingAverage(self.data, period=self.p.period)

    def next(self):
        if self.movav.lines.sma[0] > self.data.lines.close[0]:
            print('Simple Moving Average is greater than the closing price')
```
`self.movav`和`self.data`均有lines这个attribute；其中，`self.movav`的`lines`中有`sma`, `self.data`的`lines`中有`close`。而`sma`和`close`是两条数据线，可用索引去获取其中的数据点。
+ `xxx.lines` = `xxx.l`
+ `xxx.lines.name` = `xxx.lines_name`
+ `self.data_name` = `self.data.lines.name` (在`Strategy`和`Indicators`中可用)
+ `self.data1_name` = `self.data1.lines.name`
+ (最常用) `self.data.lines.close` = `self.data.close`, `self.movav.lines.sma` = `self.movav.sma`

**未理解：Setting/Assigning the lines with these two later notations is not supported**

### Lines declaration
如果自行开发`Indicator`, `Indicator`中含有的`Lines`必须要声明，且必须使用元组中的元组格式（数据线有次序）。例如：
```
class SimpleMovingAverage(Indicator):
    lines = ('sma',) # 必须加逗号
    ...
```

在这个例子中，`self.lines[0]` = `self.lines.sma`。如果有其他的数据线，则可以用索引获取。

针对在`Indicator`内部的引用，可以使用：
+ `self.line` = `self.lines[0]`
+ `self.lineX` = `self.lines[X]`
+ `self.line_X` = `self.lines[X]`

针对在外部`Strategies`的引用，则可以使用：
+ `self.dataY` = `self.data.lines[Y]`
+ `self.dataX_Y` = `self.dataX.lines[Y]` = `self.datas[X].lines[Y]`

### Accessing lines in Data Feeds
在Data Feeds中，代码上可以忽略`lines`直接调用数据线。

`self.data.close[0]` = `self.dataq.lines.close[0]`

注：该方法不适用于`Indicators`,原因在于`Indicator`可能有一个用来计算的'close
'`attribute`与数据线重名，因此会产生混淆，而在Data Feeds中并没有计算，因此可以直接引用。

### Lines len
可以用Python自带的`len`函数或是Backtrader提供的`buflen`来计量数据线的长度。具体区别为：

+ `len`报告有多少bar已经被处理了
+ `buflen`报告在Data Feeds中总共有多少bar被预装载。

如果返回同一数值，则说明：1. 数据未被预装载（都返回0）；2. 所有数据都被处理（返回总长度）。

### Indexing: 0 and -1

`Strategy`只获取数据，`Indicator`计算并建立数据。

索引0代表数据线中的现值，-1代表前一个，以此类推。如果不使用索引，默认为0（现值）。`self.movav.lines.sma > self.data.lines.close` = `self.movav.lines.sma[0] > self.data.lines.close[0]`

`Indicator`的计算如下：每一步中，计算当前数据线的值，例如一个简单均线可以写成：
```
def next(self):
  self.line[0] = math.fsum(self.data.get(0, size=self.p.period)) / self.p.period
```

### Slicing

Backtrader不支持常规切片操作，例如`myslice = self.my_sma[0:-1]`。 如果想要获取切片值，需要使用`myslice = self.my_sma.get(ago=0, size=10)`（获取最新10个值）。其中`ago`默认值为0。

### Lines: DELAYED indexing

在`next`方法中，可以通过`[]`来获取对应的个值，但是在`__init__`中，需要使用`()`来对数据线进行索引取值。例如：

```
class MyStrategy(bt.Strategy):
    params = dict(period=20)

    def __init__(self):

        self.movav = btind.SimpleMovingAverage(self.data, period=self.p.period)
        self.cmpval = self.data.close(-1) > self.sma

    def next(self):
        if self.cmpval[0]:
            print('Previous close is higher than the moving average')
```

在这个例子中，`self.data.close(-1)`中的括号代表讲数据线中的数据全部推后一位，再与`self.sma`比较，即昨日收盘价是否大于20日均线，如有，则`self.cmpval=1`，如无，则`self.cmpval=0`。

### Lines Coupling

如果需要比较不同时间跨度的数据（长度不同），可以在`__init__`方法中加入`()`但是括号里面不需要填入数字。例如需要比较日数据和周数据：

```
class MyStrategy(bt.Strategy):
    params = dict(period=20)

    def __init__(self):

        # data0 is a daily data
        sma0 = btind.SMA(self.data0, period=15)  # 15 days sma
        # data1 is a weekly data
        sma1 = btind.SMA(self.data1, period=5)  # 5 weeks sma

        self.buysig = sma0 > sma1()

    def next(self):
        if self.buysig[0]:
            print('daily sma is greater than weekly sma1')
```

由于`sma1`数据量较小, 因此加入括号实现Coupling，将其长度拷贝扩展到sma0上。

### Operators, using natural constructs

若想用逻辑运算创建额外的数据线，则除了`>`、`<`和`==`之外，在`__init__`方法中需要使用Backtrader内置的逻辑运算符(因为Python原生的`and`等不属于运算符)：

+ and -> And
+ or -> Or
+ if -> If
+ any -> Any
+ all -> All
+ cmp -> Cmp
+ max -> Max
+ min -> Min
+ sum -> Sum
+ reduce -> Reduce


例子1
```
class MyStrategy(bt.Strategy):

    def __init__(self):

        sma1 = btind.SMA(self.data.close, period=15)
        self.buysig = bt.And(sma1 > self.data.close, sma1 > self.data.high)

    def next(self):
        if self.buysig[0]:
            pass  # do something here
```

例子2
```
class MyStrategy(bt.Strategy):

    def __init__(self):

        sma1 = btind.SMA(self.data.close, period=15)
        high_or_30 = bt.If(sma1 > self.data.close, 30.0, self.data.high)
        sma2 = btind.SMA(high_or_30, period=15)
```