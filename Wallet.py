import json
from Config import BASE, INITIAL_AMOUNT, EXCHANGES
from models.Wallet import Wallet as WalletDB
from utils.coins import getCoins
from utils.patterns.classPattern import singleton


@singleton
class Wallet:

    def __init__(self):
        self.wallet = dict()
        self.load()

    def pay(self, exchange, amount, pair):
        coin, _ = getCoins(pair)
        self._check(exchange=exchange, coin=coin)
        assert self._baseIsPositive(exchange=exchange)
        discount = exchange.getDiscount()
        buyPrice = exchange.getBuyPrice(pair)
        result = amount * discount / buyPrice
        print('Compra:')
        self._addAmount(exchange=exchange, coin=coin, amount=result)
        self._subtractBase(exchange=exchange, amount=amount)
        self.save()
        return buyPrice

    def collect(self, exchange, pair):
        coin, _ = getCoins(pair)
        self._check(exchange=exchange, coin=coin)
        assert self._isPositive(exchange=exchange, coin=coin)
        amount = self._getAmount(exchange=exchange, coin=coin)
        sellPrice = exchange.getSellPrice(pair)
        discount = exchange.getDiscount()
        result = amount * sellPrice * discount
        print('Venta:')
        self._addBase(exchange=exchange, amount=result)
        self._subtractAmount(exchange=exchange, coin=coin, amount=amount)
        self.save()
        return result, sellPrice

    def transfer(self, coin, fee, exchange1, exchange2):
        print('Transferencia:')
        self._check(exchange=exchange1, coin=coin)
        self._check(exchange=exchange2, coin=coin)
        self._subtractAmount(exchange=exchange1, coin=coin, amount=fee)
        amount = self._getAmount(exchange=exchange1, coin=coin)
        self._setAmount(exchange=exchange1, coin=coin, amount=0)
        self._addAmount(exchange=exchange2, coin=coin, amount=amount)
        return self._getAmount(exchange=exchange2, coin=coin)

    def _isPositive(self, exchange, coin):
        return self._getAmount(exchange=exchange, coin=coin) > 0

    def _baseIsPositive(self, exchange):
        return self._getBase(exchange) > 0

    def _subtractAmount(self, exchange, coin, amount):
        oldAmount = self._getAmount(exchange=exchange, coin=coin)
        newAmount = oldAmount - amount
        self._setAmount(exchange=exchange, coin=coin, amount=newAmount)
        if self._getAmount(exchange=exchange, coin=coin) < 0:
            raise Exception('NegativeSubtractException')

    def _subtractBase(self, exchange, amount):
        self._subtractAmount(exchange=exchange, coin=BASE, amount=amount)

    def _addAmount(self, exchange, coin, amount):
        oldAmount = self._getAmount(exchange=exchange, coin=coin)
        newAmount = oldAmount + amount
        self._setAmount(exchange=exchange, coin=coin, amount=newAmount)

    def _addBase(self, exchange, amount):
        self._addAmount(exchange=exchange, coin=BASE, amount=amount)

    def _setAmount(self, exchange, coin, amount):
        exchange.setAmount(coin=coin, amount=amount)

    def _setBase(self, exchange, amount):
        self._setAmount(exchange=exchange, coin=BASE, amount=amount)

    def _getAmount(self, exchange, coin):
        return exchange.getAmount(coin)

    def _getBase(self, exchange):
        return self._getAmount(exchange=exchange, coin=BASE)

    @staticmethod
    def _check(exchange, coin):
        wallet = exchange.wallet
        if coin not in wallet.keys():
            exchange.setAmount(coin=coin, amount=0)

    def save(self):
        wallets = dict()
        for exchange in EXCHANGES:
            wallet = str(exchange.wallet)
            wallets[str(exchange)] = wallet

        WalletDB.create(
            wallets=wallets
        )

    def load(self):
        query = WalletDB.select().order_by(WalletDB.id.desc())
        if query.exists():
            wallet = query.get()
            wallets = wallet.wallets.replace('"', ' ')
            wallet = wallets.replace("'", '"')
            self.wallet = json.loads(wallet)
            for exchange1 in self.wallet:
                for exchange2 in EXCHANGES:
                    if exchange1 == str(exchange2):
                        exchange1 = self.wallet[exchange1]
                        for coin in exchange1.keys():
                            amount = exchange1[coin]
                            if amount > 0:
                                exchange2.setAmount(coin=coin, amount=amount)
        else:
            self._setBase(exchange=EXCHANGES[0], amount=INITIAL_AMOUNT)
            self.save()
