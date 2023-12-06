from utils.getPrecisionByStep import getPrecisionByStep
from utils.parse import parseBinance
from utils.parse import parseKucoin
from utils.trunc import trunc
from kucoin.client import User, Market, Trade
from Exchange import Exchange
from time import sleep
from datetime import datetime
import requests
from Config import KUCOIN_PUBLIC_KEY, KUCOIN_SECRET_KEY, KUCOIN_PASSPHRASE
import time
import base64
import hmac
import hashlib


class Kucoin(Exchange):

    def __init__(self):
        self.baseUrl = 'https://api.kucoin.com'
        self.client = User(KUCOIN_PUBLIC_KEY, KUCOIN_SECRET_KEY, KUCOIN_PASSPHRASE)
        self.trade = Trade(key=KUCOIN_PUBLIC_KEY, secret=KUCOIN_SECRET_KEY, passphrase=KUCOIN_PASSPHRASE, is_sandbox=False, url='https://api.kucoin.com')
        self.market = Market(url=self.baseUrl)
        super(Kucoin, self).__init__()
        self.steps = dict()
        self.setSteps()
        self.orderId = None
        self.speedNetworks = ['AVA-USDT', 'ATOM-USDT', 'FTM-USDT', 'BNB-USDT', 'CHZ-USDT', 'KSM-USDT', 'DOT-USDT', 'XLM-USDT', 'XRP-USDT', 'EOS-USDT', 'USDC-USDT', 'PHA-USDT', 'ICP-USDT', 'SOL-USDT', 'MOVR-USDT', 'EGLD-USDT', 'RUNE-USDT', 'WRX-USDT', 'KAVA-USDT', 'SRM-USDT', 'HARD-USDT', 'HNT-USDT', 'GLMR-USDT', 'GMT-USDT', 'SCRT-USDT', 'ICX-USDT', 'FIDA-USDT']

    def subscribe(self, pairs):
        assert type(pairs) is list
        #assert len(pairs) <= 100
        pairs = pairs[:100]
        response = requests.post('https://api.kucoin.com/api/v1/bullet-public').json()['data']
        token = response['token']
        endpoint = response['instanceServers'][0]['endpoint']
        url = endpoint + "?token=" + token
        pairsStr = ''
        for pair in pairs:
            pairsStr += pair + ','
        pairsStr = pairsStr[:-1]
        request = {"type": "subscribe",  "topic": f"/market/ticker:{pairsStr}"}
        subscribe(url, request, self.on_message)

    def on_message(self, msg):
        if msg['type'] == 'message':
            super(Kucoin, self).on_message(msg)
            pair = msg['topic'].replace('/market/ticker:', '')
            buy = msg['data']['bestAsk']
            sell = msg['data']['bestBid']
            buyQty = msg['data']['bestAskSize']
            sellQty = msg['data']['bestBidSize']
            self.setPrice(pair, buy, sell, buyQty, sellQty)
            self.arbitrator.run(pair)

    def buy(self, pair, amount):
        pair = parseKucoin(pair)
        step = self.steps[pair]['coin']
        precision = getPrecisionByStep(step)
        price = self.getPrice(pair=pair, mode='buy')
        amount = amount/price
        amount = trunc(amount, precision)
        response = self.trade.create_market_order(symbol=pair, side='buy', size=amount)
        print(f'Compra({self}): ', response)
        return price

    def sell(self, pair, amount):
        pair = parseKucoin(pair)
        step = self.steps[pair]['coin']
        precision = getPrecisionByStep(step)
        amount = trunc(amount, precision)
        response = self.trade.create_market_order(symbol=pair, side='sell', size=amount)
        print(f'Venta({self}): ', response)
        return self.getPrice(pair, 'sell')

    def transfer(self, coin, address, network, addressTag):
        amount = self.getRealAmount(coin)
        self.client.inner_transfer(coin, 'trade', 'main', amount)
        while self.getWallet(accountType='main')[coin] == 0:
            sleep(0.01)
        amount = trunc(amount, 6)
        result = self.client.apply_withdrawal(currency=coin, address=address, amount=amount, chain=network, memo=addressTag)
        print(f'Transferencia({self}) ID:', result)
        print(f'Transfer data:', {'network': network, 'address': address, 'addressTag': addressTag, 'coin': coin})
        print(f'Transferencia enviada a las -> {datetime.now()}')
        return result

    def waitTransfer(self, coin):
        inicio = datetime.now()
        print(f'Waiting transfer in {self}...')
        minAmount = self.getMin(coin + BASE)
        while True:
            mainWallet = self.getWallet(accountType='main')
            tradeWallet = self.getWallet()
            mainAmount = mainWallet[coin]
            tradeAmount = tradeWallet[coin]
            if tradeAmount > minAmount or mainAmount > minAmount:
                fin = datetime.now()
                delay = (fin - inicio).seconds
                time = Time(coin=coin, delay=delay)
                time.save()
                print(f'Transferencia recibida in {self} a las -> {datetime.now()}')
                print(f'Delay: {delay} seconds')
                break
            sleep(.5)
        maxAmount = max([mainAmount, tradeAmount])
        if maxAmount == mainAmount:
            self.client.inner_transfer(coin, from_payer='main', to_payee='trade', amount=mainAmount)
            sleep(1)
        return maxAmount

    def getPairs(self):
        pairs = self.market.get_symbol_list()
        pairs = [pair['name'] for pair in pairs]
        return pairs

    def getAllCoins(self):
        response = self.market.get_symbol_list()
        coins = dict()
        for pair in response:
            coin = pair['baseCurrency']
            base = pair['quoteCurrency']
            coins.update({parseBinance(pair['name']): {'coin': coin, 'base': base}})
        return coins

    def getWallet(self, accountType='trade'):
        self.walletLock.acquire()
        response = self.client.get_account_list()
        wallet = dict()
        if type(response) is list:
            [wallet.update({account['currency']: float(account['available'])}) for account in response if account['type'] == accountType]
        self.walletLock.release()
        return wallet

    def getNetwork(self, coin):
        if coin in self.networks.keys():
            self.networkLock.acquire()
            network = self.networks[coin]
            self.networkLock.release()
            return network

        self.networkLock.acquire()
        response = self.market.get_currency_detail_v2(coin)['chains']
        networks = dict()
        for chain in response:
            name = chain['chain']
            confirm = chain['confirms']
            if self.filterSpeedNetwork(name):
                networks.update({name: {
                    'min': float(chain['withdrawalMinSize']),
                    'enabled': chain['isWithdrawEnabled'],
                    'fee': float(chain['withdrawalMinFee']),
                    'confirm': confirm
                }})
        self.networks.update({coin: networks})
        self.networkLock.release()
        return networks

    def getAddress(self, coin, network):
        network = network.lower()
        response = self.client.get_deposit_addressv2(currency=coin, chain=network)
        if type(response) == dict:
            response = [self.client.create_deposit_address(coin, network)]
        response = response[0]
        return {'address': response['address'], 'addressTag': response['memo']}

    def getAmount(self, coin):
        if coin in self.wallet.keys():
            return super(Kucoin, self).getAmount(coin)
        return self.getRealAmount(coin)

    def setCommission(self):
        commission = self.client.get_base_fee()['takerFeeRate']
        self.commission = float(commission)

    def setMins(self):
        mins = dict()
        response = self.market.get_symbol_list()
        for pair in response:
            minAmount = pair['minFunds']
            if minAmount is None:
                continue
            minAmount = float(minAmount)
            name = parseBinance(pair['name'])
            mins.update({name: minAmount})
        super(Kucoin, self)._setMins(mins)

    def setSteps(self):
        response = self.market.get_symbol_list()
        for pair in response:
            self.steps.update({pair['symbol']: {'coin': pair['baseIncrement'], 'base': pair['quoteIncrement']}})

    @staticmethod
    def _getHeaders(endpoint, method):
        now_time = int(time.time()) * 1000
        str_to_sign = str(now_time) + method + endpoint
        sign = base64.b64encode(hmac.new(KUCOIN_SECRET_KEY.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
        headers = {
            "KC-API-SIGN": sign,
            "KC-API-TIMESTAMP": str(now_time),
            "KC-API-KEY": KUCOIN_PUBLIC_KEY,
            "KC-API-PASSPHRASE": KUCOIN_PASSPHRASE,
            "Content-Type": "application/json"
        }
        return headers

    def getOrderBook(self, pair):
        endpoint = f'/api/v3/market/orderbook/level2?symbol={parseKucoin(pair)}'
        headers = self._getHeaders(endpoint=endpoint, method='GET')
        url = f'{self.baseUrl}{endpoint}'
        book = requests.get(url=url, headers=headers).json()['data']
        bids, asks = book['bids'], book['asks']
        bids = [[float(element) for element in sublist] for sublist in bids]
        asks = [[float(element) for element in sublist] for sublist in asks]
        return bids, asks


