from abc import ABC, abstractmethod
from threading import Lock
from utils.parse import parseBinance
from utils.coins import getCoins
from Config import BASE
from datetime import datetime
from time import sleep


class Exchange(ABC):

    def __init__(self):
        self.arbitrator = None
        self.wallet = dict()  # Almacena los montos disponibles de cada crypto.
        self.mins = dict()  # Almacena el monto mínimo de tradeo para cada par.
        self.lastUpdate = None
        self.commission = float()  # Comisión que cobra el exchange por operación de compra o venta

        # Locks
        self.walletLock = Lock()
        self.updateLock = Lock()

        # Setters
        self.setCommission()
        self.discount = 1-self.commission
        self.setWallet()
        self.setMins()

    def setArbitrator(self, arbitrator):
        self.arbitrator = arbitrator

    # Almacena el monto disponible de una crypto
    def setAmount(self, coin, amount):
        print(f'Actualizando monto {self}->{coin}: {amount}')
        self.walletLock.acquire()
        self.wallet[coin] = amount
        self.walletLock.release()

    # Retorna el monto disponible almacenado
    def getAmount(self, coin):
        self.walletLock.acquire()
        if coin in self.wallet.keys():
            amount = self.wallet[coin]
        else:
            amount = 0
        self.walletLock.release()
        return amount

    # Almacena todos los montos de la cuenta
    def setWallet(self):
        print(f'Actualizando billetera de {self}')
        wallet = self.getWallet()
        print(f'Wallet({self})->{wallet[BASE]} {BASE}')
        self.walletLock.acquire()
        self.wallet = wallet
        self.walletLock.release()

    # Obtiene el monto disponible real disponible en la cuenta
    def getRealAmount(self, coin):
        wallet = self.getWallet()
        if coin in wallet.keys():
            return wallet[coin]
        else:
            return 0

    # Almacena el precio notificado por el websocket
    def setPrice(self, pair, buy, sell, buyQty, sellQty):
        pair = parseBinance(pair)
        exchange = str(self)
        self.pricesLock.acquire()
        self.prices[pair] = {'buy': float(buy), 'sell': float(sell), 'buyQty': float(buyQty) * float(buy), 'sellQty': float(sellQty) * float(sell), 'time': datetime.now()}
        self.pricesLock.release()

    # Retorna el descuento del exchange
    def getDiscount(self):
        return self.discount

    # Retorna el monto mínimo de tradeo
    def getMin(self, pair):
        pair = parseBinance(pair)
        assert pair in self.mins.keys()
        pair = parseBinance(pair)
        return self.mins[pair]

    def _setMins(self, mins):
        print(f'Almacenando mínimos de {self}')
        self.mins = mins

    # Empareja las redes de dos exchanges
    def matchNetwork(self, exchange, coin):
        try:
            networks1 = self.getNetwork(coin)
            networks2 = exchange.getNetwork(coin)
        except AssertionError:
            return None
        names = [name.lower() for name in networks2.keys() if networks2[name]['enabled'] is True]
        network = {'fee': float('inf')}
        for name in networks1.keys():
            if name.lower() in names:
                if networks1[name]['fee'] < network['fee'] and networks1[name]['enabled'] is True:
                    network = networks1[name].copy()
                    network.update({'name': name})
        if 'name' not in network.keys():
            return None
        return network

    # Empareja los pares de dos exchanges
    def matchPairs(self, exchanges):
        print(f'Detectando redes rápidas de {self}')
        if self.speedNetworks is not None:
            print(self, len(self.speedNetworks), 'criptomonedas')
            return self.speedNetworks
        pairs = list()
        selfPairs = list()
        for exchange in exchanges:
            if exchange is not self:
                for pair in exchange.getPairs():
                    pairs.append(parseBinance(pair))
        for pair in self.getPairs():
            if parseBinance(pair) in pairs:
                coin, base = getCoins(pair)
                try:
                    if base == BASE:
                        network = self.getNetwork(coin)
                        if len(network) > 0:
                            selfPairs.append(pair)
                except AssertionError:
                    continue
        print(self, len(selfPairs), 'criptomonedas')
        return selfPairs

    def waitTrade(self, coin, withdrawMin):
        print(f'Waiting trade in {self}...')
        while True:
            newAmount = self.getRealAmount(coin)
            if withdrawMin < newAmount:
                print(f'Trade realizado en {self} a las -> {datetime.now()}')
                return newAmount
            sleep(.5)

    def __str__(self):
        return self.__class__.__name__

    def getLastUpdate(self):
        self.updateLock.acquire()
        lastUpdate = self.lastUpdate
        self.updateLock.release()
        return lastUpdate

    # Métodos abstractos

    @abstractmethod
    def buy(self, pair, amount):
        pass

    @abstractmethod
    def sell(self, pair, amount):
        pass

    # Devuelve todos los pares disponibles del exchange
    @abstractmethod
    def getPairs(self):
        pass

    # Devuelve todas las monedas disponibles del exchange
    @abstractmethod
    def getAllCoins(self):
        pass

    # Devuelve el estado de la billetera de la cuenta
    @abstractmethod
    def getWallet(self):
        pass

    # Retorna el order book para un par dado
    @abstractmethod
    def getOrderBook(self, pair):
        pass

    @abstractmethod
    def setMins(self):
        pass

    @abstractmethod
    def setCommission(self):
        pass
