from utils.parse import parseBinance
from utils.coins import getCoins
from datetime import datetime


class Chance:

    def __init__(self, pair, buyPrice, sellPrice, exchange, buyQty, sellQty, amount):
        self.pair = parseBinance(pair)
        self.coin, self.base = getCoins(pair)
        self.buyPrice = buyPrice
        self.sellPrice = sellPrice
        self.exchange = exchange
        self.buyQty = buyQty
        self.sellQty = sellQty
        self.amount = amount
        self.mode = None
        self.initTime = datetime.now()

    def __str__(self):
        msg = '-' * 50 + '\n'
        msg += f'Hora: {datetime.now()}' + '\n'
        msg += f'Pair: {self.pair}' + '\n'
        msg += f'Compra: {self.buyPrice} Venta: {self.sellPrice}' + '\n'
        msg += f'BuyQty: {self.buyQty} SellQty: {self.sellQty}' + '\n'
        msg += f'Amount: {self.amount}' + '\n'
        msg += f'Exchange: {self.exchange}' + '\n'
        msg += '-' * 50
        return msg
