# Desacoplar Trader de Wallet
# Reformular Wallet
# Muevo exchanges debe quedar igual
# Los fee estan en unidad cripto, deben transformarse en el geogebra, creo. Las ecuaciones contemplaban eso?
# Verify Results debe contrastar solo contra el monto que se tradeo, no con todo lo que hay en la cuenta

from utils.coins import setCoins
from utils.setArbitrator import setArbitrator
from Arbitrator import Arbitrator
from threading import Thread
from Telegram import BotTelegram
from Wallet import Wallet
from Binance import Binance
from Kucoin import Kucoin
from Config import IS_REAL_TRADER, EXCHANGES, COINS
from Tester import Tester

telegram = BotTelegram()
binance = Binance()
#kucoin = Kucoin()
EXCHANGES.append(binance)
#EXCHANGES.append(kucoin)

if not IS_REAL_TRADER:
    wallet = Wallet()

setCoins()

arbitrator = Arbitrator(telegram)
setArbitrator(arbitrator)
telegram.setArbitrator(arbitrator)

threads = list()
for exchange in EXCHANGES:
    pairs = exchange.getPairs()
    print('Numero de pares:', len(pairs))
    thread = Thread(target=arbitrator.run, args=[pairs, exchange], name=f'{exchange}-Thread')
    threads.append(thread)

# Telegram Thread
threadTelegram = Thread(target=telegram.run, name='Telegram-Thread')
threadTelegram.daemon = True
#threads.append(threadTelegram)

# Tester Thread
threadTester = Tester(arbitrator=arbitrator, exchanges=EXCHANGES, threads=threads, telegram=telegram, name='Tester-Thread')
threadTester.daemon = True
threads.append(threadTester)

threadTester.turnOn()
threadTelegram.run()

# No debería llegar
for thread in threads:
    thread.join()
