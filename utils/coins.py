from Config import COINS, EXCHANGES, setCoinsConfig
import utils.parse as parse


def setCoins():
    coins = dict()
    for exchange in EXCHANGES:
        coins.update(exchange.getAllCoins())
    setCoinsConfig(coins)


def getCoins(pair):
    pair = parse.parseBinance(pair)
    assert pair in COINS.keys(), Exception('UnknownPairException')
    return COINS[pair]['coin'], COINS[pair]['base']
