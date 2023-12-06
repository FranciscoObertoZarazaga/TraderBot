import requests

from Config import BINANCE_PUBLIC_KEY, BINANCE_SECRET_KEY, BASE
from utils.parse import parseBinance
from utils.trunc import trunc
from binance.client import Client
from binance.exceptions import BinanceAPIException
from Exchange import Exchange
from utils.getPrecisionByStep import getPrecisionByStep
from time import sleep
from datetime import datetime


class Binance(Exchange):

    def __init__(self):
        self.client = Client(BINANCE_PUBLIC_KEY, BINANCE_SECRET_KEY)
        super(Binance, self).__init__()

    def getNow(self, pair):
        orderBook = self.client.get_order_book(symbol=pair, limit="1")
        assert len(orderBook['asks']) > 0 and len(orderBook['bids']) > 0, 'VoidOrderBookException'
        buyPrice = float(orderBook['asks'][0][0])
        sellPrice = float(orderBook['bids'][0][0])
        buyQty = float(orderBook['asks'][0][1]) * buyPrice
        sellQty = float(orderBook['bids'][0][1]) * sellPrice
        # return buyPrice, sellPrice, buyQty, sellQty
        return buyPrice, sellPrice, buyQty, sellQty

    def getBuyPrice(self, pair):
        buyPrice, _, _, _ = self.getNow(pair)
        return buyPrice

    def getSellPrice(self, pair):
        _, sellPrice, _, _ = self.getNow(pair)
        return sellPrice

    def buy(self, pair, amount):
        pair = parseBinance(pair)
        precision = self.client.get_symbol_info(pair)['quoteAssetPrecision']
        amount = trunc(amount, precision)
        try:
            response = self.client.order_market_buy(symbol=pair, quoteOrderQty=amount)
        except BinanceAPIException as e:
            price = self.getPrice(pair, 'buy')
            amount = amount * self.discount / price
            step = float(self.client.get_symbol_info(pair)['filters'][1]['stepSize'])
            precision = getPrecisionByStep(step)
            amount = trunc(amount, precision)
            response = self.client.order_market_buy(symbol=pair, quantity=amount)
        print(f'Compra({self}): ', response['orderId'])
        return self.getPrice(pair, 'buy')

    def sell(self, pair, amount):
        pair = parseBinance(pair)
        step = float(self.client.get_symbol_info(pair)['filters'][1]['stepSize'])
        precision = getPrecisionByStep(step)
        amount = trunc(amount, precision)
        response = self.client.order_market_sell(symbol=pair, quantity=amount)
        print(f'Venta({self}): ', response['orderId'])
        return self.getPrice(pair, 'sell')

    def setLimit(self, pair, amount, price):
        pair = parseBinance(pair)
        step = float(self.client.get_symbol_info(pair)['filters'][1]['stepSize'])
        priceStep = float(self.client.get_symbol_info(pair)['filters'][0]['tickSize'])
        precision = getPrecisionByStep(step)
        amount = trunc(amount, precision)
        pricePrecision = getPrecisionByStep(priceStep)
        price = trunc(price, pricePrecision)
        response = self.client.order_limit_sell(symbol=pair, quantity=amount, price=price)
        print(f'Limit set({self}) ID:', response['orderId'])

    def removeLimit(self, pair):
        orders = self.client.get_open_orders(symbol=pair)
        for order in orders:
            orderId = order['orderId']
            self.client.cancel_order(symbol=pair, orderId=orderId)
        print(f'Order Limit eliminada en {self}')

    def waitLimit(self, pair, amount):
        response = self.client.get_open_orders(symbol=pair)
        initTime = datetime.now()
        while len(response) > 0:
            if (datetime.now() - initTime).seconds / 60 > 1:
                self.removeLimit(pair)
                self.sell(pair, amount)
                return 0
            sleep(.5)
            response = self.client.get_open_orders(symbol=pair)
        print(f'Order Limit ejecutada en {self}')
        return 1

    def getPairs(self):
        pairs = self.client.get_all_tickers()
        pairs = [pair['symbol'] for pair in pairs if pair['symbol'].endswith(BASE)]
        return pairs

    def getAllCoins(self):
        response = requests.get('https://api.binance.com/api/v3/exchangeInfo')
        response = response.json()
        data = response['symbols']
        coins = dict()
        for pair in data:
            coin = pair['baseAsset']
            base = pair['quoteAsset']
            coins.update({pair['symbol']: {'coin': coin, 'base': base}})
        return coins

    def setCommission(self):
        self.commission = float(self.client.get_account()['commissionRates']['taker'])

    def getWallet(self):
        self.walletLock.acquire()
        response = self.client.get_account()['balances']
        wallet = dict()
        for coin in response:
            wallet.update({coin['asset']: float(coin['free'])})
        self.walletLock.release()
        return wallet

    def getMin(self, pair):
        pair = parseBinance(pair)
        if pair in self.mins.keys():
            return super(Binance, self).getMin(pair)
        response = self.client.get_symbol_info(pair)
        info = response['filters'][6]
        assert info['filterType'] == 'NOTIONAL'
        minAmount = float(info['minNotional'])
        self.mins.update({pair: minAmount})
        return minAmount

    def setMins(self):
        pass

    def getOrderBook(self, pair):
        book = self.client.get_order_book(symbol=parseBinance(pair), limit=1000)
        bids, asks = book['bids'], book['asks']
        bids = [[float(element) for element in sublist] for sublist in bids]
        asks = [[float(element) for element in sublist] for sublist in asks]
        return bids, asks

    def getKlines(self, limit, interval, pair):
        return self.client.get_klines(symbol=pair, interval=interval, limit=limit)

    def getHistoricalKlines(self, pair, interval, start_str, end_str=None):
        return self.client.get_historical_klines(pair, interval, start_str, end_str)
