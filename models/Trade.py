from peewee import *
from models.BaseModel import BaseModel


class Trade(BaseModel):
    inicial = CharField()
    final = CharField()
    reward = CharField()
    buy_price = CharField()
    sell_price = CharField()
    buy_time = DateTimeField()
    sell_time = DateTimeField()
    pair = CharField()
    exchange = CharField()
