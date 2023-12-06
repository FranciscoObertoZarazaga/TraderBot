from models.Trade import Trade as TradeDB
from playhouse.shortcuts import model_to_dict
from utils.parse import parseBinance
from datetime import datetime
from Config import BASE, INITIAL_AMOUNT
from Config import EXCHANGES
import pandas as pd


class Trade:

    def __init__(self, init, end, buyPrice, sellPrice, buyTime, sellTime, chance):
        self.init = init
        self.end = end
        self.reward = None
        self.buyPrice = buyPrice
        self.sellPrice = sellPrice
        self.buyTime = buyTime
        self.sellTime = sellTime
        self.pair = parseBinance(chance.pair)
        self.exchange = chance.exchange

    def close(self, end, sellPrice):
        self.end = end
        self.sellPrice = sellPrice
        self.sellTime = datetime.now()
        self.reward = end / self.init

    def getTradeAsDict(self):
        return {
            'final': self.end,
            'inicial': self.init,
            'reward': self.reward,
            'buy_price': self.buyPrice,
            'sell_price': self.sellPrice,
            'buy_time': self.buyTime,
            'sell_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'pair': self.pair,
            'exchenge': self.exchange
        }

    def add(self):
        TradeDB.create(
            inicial=self.init,
            final=self.end,
            reward=self.reward,
            buy_price=self.buyPrice,
            sell_price=self.sellPrice,
            buy_time=self.buyTime,
            sell_time=self.sellTime,
            pair=self.pair,
            exchange=self.exchange
        )


class Trades:

    columns = ['id', 'inicial', 'final', 'reward', 'buy_price', 'sell_price', 'buy_time', 'sell_time', 'pair', 'exchange']

    def __init__(self):
        pass

    @staticmethod
    def getTradesAsDf():
        trades = Trades.getTradesAsDict()
        trades = pd.DataFrame(trades, columns=Trades.columns)
        trades = trades.sort_values(by=['buy_time'], ignore_index=True)
        trades[['final', 'inicial', 'reward', 'buy_price', 'sell_price']] = trades[['final', 'inicial', 'reward', 'buy_price', 'sell_price']].astype(float)
        return trades

    @staticmethod
    def getTradesAsDict():
        trades = Trades.getTradesFromDB()
        trades = [model_to_dict(trade) for trade in trades]
        return trades

    @staticmethod
    def getTradesFromDB():
        trades = TradeDB.select().execute()
        return trades

    def __str__(self):
        trades = Trades.getTradesAsDf()
        if len(trades) == 0:
            return 'NO SE REALIZÓ NINGÚN TRADE.'
        trades['reward'] = trades['final'] / trades['inicial']
        trades['tasa'] = trades['reward'] - 1
        n_trades = len(trades['reward'])
        n_positive_trades = len(trades[trades['reward'] >= 1])
        n_negative_trades = n_trades - n_positive_trades
        positive_rate = trades[trades['tasa'] >= 0]['tasa'].mean() * 100 if len(trades[trades['tasa'] >= 0]) > 0 else 0
        negative_rate = trades[trades['tasa'] < 0]['tasa'].mean() * 100 if len(trades[trades['tasa'] < 0]) > 0 else 0
        mean_rate = trades['tasa'].mean() * 100
        rendimiento = mean_rate * n_trades
        finalAmount = sum([exchange.getAmount(BASE) for exchange in EXCHANGES])
        initialAmount = INITIAL_AMOUNT
        tasa_de_ganancia = (finalAmount / initialAmount)
        initTime = trades['buy_time'][0]
        endTime = datetime.now()
        time = endTime - initTime
        days = time.days + time.seconds / (24 * 60 ** 2)
        rendimiento_diario = round(rendimiento / days, 2)
        rendimiento_mensual = round(rendimiento_diario * 30, 2)
        rendimiento_anual = round(rendimiento_diario * 365, 2)

        msg = '=' * 30 + '\n' + "{:^50}".format('RESULTADO') + '\n' + '=' * 30 + '\n'

        trades['absoluteReward'] = trades['final'] - trades['inicial']
        totalReward = trades.loc[trades['absoluteReward'] > 0, 'absoluteReward'].sum()
        totalLoss = trades.loc[trades['absoluteReward'] < 0, 'absoluteReward'].sum()
        ganancia_bruta = totalReward
        ganancia_neta = totalReward+totalLoss
        try:
            assert n_trades > 0
            tasa_de_aciertos = 100 * (ganancia_bruta/(ganancia_bruta+abs(totalLoss)))
        except (ZeroDivisionError, AssertionError):
            return "NO SE REALIZÓ NINGÚN TRADE."

        titulo = [
            'Monto Inicial',
            'Monto Final',
            'Ganancia Bruta',
            'Pérdida',
            'Ganancia Neta',
            'Acertabilidad',
            'Multiplicador',
            'N° de Trades',
            'N° de Trades Positivos',
            'N° de Trades Negativos',
            'Tasa de Aciertos',
            'Tasa Promedio',
            'Tasa de Ganancia Promedio',
            'Tasa de Pérdida Promedio',
            'Rendimiendo Medio',
            'Rendimiendo Medio Diario',
            'Rendimiendo Medio Mensual',
            'Rendimiendo Medio Anual',
            'Tiempo'
        ]
        valor = [
            initialAmount,
            finalAmount,
            ganancia_bruta,
            totalLoss,
            ganancia_neta,
            tasa_de_aciertos,
            tasa_de_ganancia,
            n_trades,
            n_positive_trades,
            n_negative_trades,
            n_positive_trades / n_negative_trades if n_negative_trades > 0 else float('inf'),
            mean_rate,
            positive_rate,
            negative_rate,
            rendimiento,
            rendimiento_diario,
            rendimiento_mensual,
            rendimiento_anual,
            days
        ]

        unidad = ['USDT', 'USDT', 'USDT', 'USDT', 'USDT', '%', '', '', '', '', 'P/N', '%', '%', '%', '%', '%', '%', '%',
                  'Días']
        for i, t in enumerate(titulo):
            msg += f'\n{t}:\n{valor[i]:.2f} {unidad[i]: <5}\n'
            msg += '.' * 50 + '\n' if i < len(titulo) - 1 else '\n' + '=' * 30 + '\n'

        return msg
