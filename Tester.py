import threading
from threading import Thread
from datetime import datetime
from time import sleep
from utils.config.setters import setTurnOff
import requests


class Tester(Thread):
    
    def __init__(self, arbitrator, exchanges, threads, telegram, name):
        super(Tester, self).__init__(name=name)
        self.arbitrator = arbitrator
        self.arbitratorLock = self.arbitrator.arbitratorLock
        self.exchanges = exchanges
        self.threads = threads
        self.telegram = telegram
     
    def run(self):
        while True:
            for exchange, thread in zip(self.exchanges, self.threads):
                lastUpdate = self.getUpdate(exchange)
                if self.checkUpdate(lastUpdate) or not thread.is_alive() or not self.ping():
                    self.restart()
            sleep(1)

    @staticmethod
    def checkUpdate(update):
        if update is not None:
            difference = (datetime.now() - update).seconds
            return not difference == 0
        return 0

    @staticmethod
    def getUpdate(exchange):
        return exchange.getLastUpdate()

    def turnOn(self):
        setTurnOff(False)
        for thread in self.threads:
            if not thread.is_alive():
                thread.start()
        print('Running...')

    @staticmethod
    def turnOff():
        setTurnOff(True)

    def restart(self):
        self.arbitratorLock.acquire()
        print('!' * 10, 'RECONNECTING', '!' * 10)
        print(f'Time: {datetime.now()}')
        try:
            self.turnOff()
            self.awaitTurnOff()
            self.reconect()
            self.resetThreads()
            self.turnOn()
            self.awaitTurnOn()
        except:
            pass
        finally:
            print('!' * 10, 'RECONNECTED', '!' * 10)
            self.arbitratorLock.release()

    def awaitTurnOff(self):
        while True:
            state = [thread.is_alive() for thread in self.threads if thread is not threading.current_thread()]
            if 1 not in state:
                return
            sleep(1)

    def awaitTurnOn(self):
        for exchange, thread in zip(self.exchanges, self.threads):
            lastUpdate = self.getUpdate(exchange)
            while self.checkUpdate(lastUpdate):
                sleep(1)
                assert self.ping() and thread.is_alive()
                lastUpdate = self.getUpdate(exchange)

    @staticmethod
    def reconect():
        while not Tester.ping():
            sleep(3)

    @staticmethod
    def ping():
        try:
            requests.get("https://www.google.com")
            return True
        except (requests.ConnectionError, requests.Timeout):
            return False

    def resetThreads(self):
        threads = list()
        for exchange in self.exchanges:
            pairs = exchange.matchPairs(self.exchanges)
            thread = Thread(target=self.arbitrator.run, args=[pairs], name=f'{exchange}-Thread')
            threads.append(thread)
        self.threads = threads
