from threading import Lock
from dotenv import load_dotenv
from binance.enums import *
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Database
DATABASE_NAME = os.getenv('DATABASE_NAME')
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_PORT = os.getenv('DATABASE_PORT')

# Binance Keys
BINANCE_PUBLIC_KEY = os.getenv('BINANCE_PUBLIC_KEY')
BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')

# Kucoin Keys
KUCOIN_PUBLIC_KEY = os.getenv('KUCOIN_PUBLIC_KEY')
KUCOIN_SECRET_KEY = os.getenv('KUCOIN_SECRET_KEY')
KUCOIN_PASSPHRASE = os.getenv('KUCOIN_PASSPHRASE')

# Telegram Keys
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_USER_ID = os.getenv('TELEGRAM_USER_ID')

IS_REAL_TRADER = False
TURN_OFF = False
TURN_OFF_LOCK = Lock()

BASE = 'USDT'
TEST_AMOUNT = 1000
REAL_AMOUNT = 1000
INITIAL_AMOUNT = REAL_AMOUNT if IS_REAL_TRADER else TEST_AMOUNT

COINS = dict()
EXCHANGES = list()

INTERVAL = KLINE_INTERVAL_15MINUTE


def setCoinsConfig(coins):
    global COINS
    COINS.update(coins)