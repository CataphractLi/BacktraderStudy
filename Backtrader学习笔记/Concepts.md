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