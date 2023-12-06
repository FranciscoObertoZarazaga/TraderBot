
class BookSimulator:

    @staticmethod
    def buy(amount, exchange, pair):
        _, asks = exchange.getOrderBook(pair)
        buyed = 0
        order = 0
        while amount > 0:
            # Volume in Crypto Unit
            # Amount in Base Unit
            price, volume = asks[order]
            volume = volume * price  # Crypto to Base convertion
            volume = amount if amount < volume else volume
            buyed += volume/price

            order += 1
            amount -= volume
        return buyed

    @staticmethod
    def sell(amount, exchange, pair):
        bids, _ = exchange.getOrderBook(pair)
        selled = 0
        order = 0
        while amount > 0:
            # Volume in Crypto Unit
            # Amount in Crypto Unit
            price, volume = bids[order]
            volume = amount if amount < volume else volume
            selled += volume*price

            order += 1
            amount -= volume
        return selled

