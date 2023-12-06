import utils.coins as coins


def parseBinance(pair):
    return pair.replace('-', '')


def parseKucoin(pair):
    coin, base = coins.getCoins(pair)
    return f'{coin}-{base}'


