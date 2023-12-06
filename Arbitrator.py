import threading
from datetime import datetime
from threading import Lock
from utils.arbitrator.verify import *
from Config import IS_REAL_TRADER, INTERVAL
from Klines import Klines
from Log import Log
from utils.simulation import simulate
from Trade import Trade
from Chance import Chance
from Strategy import squeeze_strategy
from time import sleep


class Arbitrator:

    def __init__(self, telegram):
        self. telegram = telegram
        self.log = Log()
        self.arbitratorLock = Lock()  # Recordar que este lock aparece en la calse Tester
        self.updateLock = Lock()
        self.lastUpdate = None
        self.trades = dict()

    def run(self, pairs, exchange):
        while True:
            for pair in pairs:
                try:
                    # Obtiene información
                    buyPrice, sellPrice, buyQty, sellQty = exchange.getNow(pair)
                    amount = exchange.getAmount(BASE)

                    chance = Chance(
                        pair=pair,
                        buyPrice=buyPrice,
                        sellPrice=sellPrice,
                        exchange=exchange,
                        buyQty=buyQty,
                        sellQty=sellQty,
                        amount=amount
                    )

                    kl = Klines(exchange).get(interval=INTERVAL, pair=pair)
                    operation = squeeze_strategy(df=kl)
                    self.do(operation, chance)

                except AssertionError:
                    continue
                except Exception as e:
                    print('-'*50 + '\n' + f'{pair}: ' + str(e) + '\n' + '-'*50)
                finally:
                    self.setLastUpdate()
                    #sleep(0)

    def do(self, operation, chance):
        key = f'{chance.pair}-{chance.exchange}'
        if operation == 1 and len(self.trades.keys()) == 0:
            chance.mode = 'buy'
            self.execute(chance)
            self.trades[key] = Trade(
                init=chance.amount,
                end=None,
                buyPrice=chance.buyPrice,
                sellPrice=None,
                buyTime=datetime.now(),
                sellTime=None,
                chance=chance
            )

        elif operation == -1 and key in self.trades.keys():
            chance.mode = 'sell'
            finalAmount = self.execute(chance)
            trade = self.trades[key]
            trade.close(end=finalAmount, sellPrice=chance.sellPrice)
            trade.add()
            print(f'OBTUVO {round(finalAmount - trade.init, 2)} de {BASE} (x{round(finalAmount / trade.init, 2)})')
            self.trades.pop(key)

    def execute(self, chance):
        pair = chance.pair
        if self.arbitratorLock.acquire(False):
            try:
                # Imprime la oportunidad de Trading
                print(chance)

                # Verifica que querramos realizar el arbitraje
                if IS_REAL_TRADER:
                    # Tradea y verifica la operación
                    pass
                else:
                    # Simula la operación en una billetera ficticia
                    finalAmount = simulate(chance)
                    return finalAmount
            except AssertionError as e:
                pass
            except Exception as e:
                msg = f'EXECUTE-ERROR({pair}): ' + str(e)
                print('-'*50 + '\n' + msg + '\n' + '-'*50)
                self.telegram.notify(msg)
            finally:
                self.arbitratorLock.release()

    def setLastUpdate(self):
        self.updateLock.acquire()
        lastUpdate = f'LAST UPDATE: {datetime.now().strftime("%d/%m/%Y, %H:%M:%S")}'
        lastUpdate += f'\nTHREAD: {threading.current_thread().name}'
        self.lastUpdate = {'msg': lastUpdate, 'time': datetime.now()}
        self.updateLock.release()

    def getLastUpdateMsg(self):
        self.updateLock.acquire()
        lastUpdate = self.lastUpdate['msg'] if self.lastUpdate is not None else 'El análisis no ha iniciado.'
        self.updateLock.release()
        return lastUpdate

    def getLastUpdateTime(self):
        self.updateLock.acquire()
        lastUpdate = self.lastUpdate['time'] if self.lastUpdate is not None else None
        self.updateLock.release()
        return lastUpdate
