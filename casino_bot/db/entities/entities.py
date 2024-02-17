from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase

from casino_bot.db.entities import Entity


class User(Entity):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)
    balance = Column('balance', Integer)

    def __init__(self, id, balance):
        self.id = id
        self.balance = balance
