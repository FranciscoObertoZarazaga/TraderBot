from Config import BASE


def verifyAmount(chance):
    # Verifica que el exchange tenga monto suficiente para realizar la operación
    exchange = chance.exchange
    pair = chance.pair
    amount = exchange.getAmount(BASE)
    minAmount = exchange.getMin(pair)
    assert amount > minAmount, Exception(f'MinAmount{exchange}Exception')
    return amount


def verifyResult(chance):
    exchange = chance.exchange
    base = chance.base
    finalAmount = exchange.getRealAmount(base)
    initialAmount = chance.amount
    print('#' * 50)
    print(f'RESULTADO {round((finalAmount/initialAmount-1)*100, 2)} % en {base}')
    print('#' * 50)
