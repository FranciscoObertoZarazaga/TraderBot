from peewee import *
from models.BaseModel import BaseModel


class Wallet(BaseModel):
    wallets = TextField()

