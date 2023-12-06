from threading import Lock
from datetime import datetime
from time import sleep
from Config import IS_REAL_TRADER, BASE
from Wallet import Wallet
from Trade import Trade


def simulate(chance):
    # Verifica que sea una simulacion
    assert not IS_REAL_TRADER

    # Define variables
    exchange = chance.exchange
    pair = chance.pair
    mode = chance.mode
    initialAmount = exchange.getAmount(BASE)
    finalAmount = 0
    wallet = Wallet()

    print('#' * 10, 'SIMULATION', '#' * 10)

    if mode == 'buy':  # Compra
        wallet.pay(exchange=exchange, amount=initialAmount, pair=pair)

    elif mode == 'sell':  # Venta
        finalAmount, sellPrice = wallet.collect(exchange=exchange, pair=pair)

    print('#' * 10, 'END SIMULATION', '#' * 10)

    return finalAmount
