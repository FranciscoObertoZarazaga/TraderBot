from datetime import datetime
from Binance import Binance
from indicators.SqueezeMomentumIndicator import squeeze_momentum_indicator
from indicators.Indicator import *
import pandas as pd


class Klines:
    def __init__(self, exchange):
        self.klines = pd.DataFrame()
        self.exchange = exchange

    def load(self, interval, pair, limit=43, all=False):
        self._download(pair=pair, limit=limit, interval=interval, all=all)
        self.klines = self.klines.set_index('Time')
        #self.klines.index = pd.to_datetime(self.klines.index)
        self._calculate()
        self.klines.dropna(inplace=True)

    def get(self, interval, pair):
        self.load(interval=interval, pair=pair)
        return self.klines

    def getAll(self, interval, pair):
        self.load(interval=interval, all=True, pair=pair)
        return self.klines

    def _download(self, pair, limit, interval, all):
        columns = [
            'Time',
            'Open',
            'High',
            'Low',
            'Close',
            'Volume',
            'ignore',
            'ignore',
            'ignore',
            'ignore',
            'ignore',
            'ignore'
        ]
        times = list()
        if all:
            self.klines = pd.DataFrame(self.exchange.getHistoricalKlines(interval=interval, pair=pair, start_str='2015'), columns=columns)
        else:
            self.klines = pd.DataFrame(self.exchange.getKlines(limit=limit, interval=interval, pair=pair), columns=columns)

        self.klines['times'] = self.klines['Time']
        [times.append(datetime.fromtimestamp(int(str(time))/1000).strftime('%H:%M %d-%m-%Y')) for time in self.klines['Time']]
        self.klines['Time'] = times
        self.klines = self.klines.drop(['ignore', 'ignore', 'ignore', 'ignore', 'ignore', 'ignore'], axis=1)
        self.klines['mean'] = self.klines['Close'].rolling(window=20).mean()
        self.klines[['Open', 'High', 'Low', 'Close', 'Volume', 'mean']] = self.klines[['Open', 'High', 'Low', 'Close', 'Volume', 'mean']].astype(float)

    def _calculate(self):
        self.klines['sm'] = squeeze_momentum_indicator(self.klines)
