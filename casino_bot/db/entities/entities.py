import sqlalchemy.dialects.postgresql
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import psycopg2
from sqlalchemy.orm import DeclarativeBase, relationship

from casino_bot.db.entities import Entity


class User(Entity):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    balance = Column(psycopg2.sqltypes.BIGINT)

    # Добавляем поле для связи с объектом Chat
    chat_id = Column(psycopg2.sqltypes.BIGINT, ForeignKey('chats.id'))
    chat = relationship("Chat", back_populates="users")  # Обратная связь

    def __init__(self, id, username, balance, chat_id):
        self.id = id
        self.balance = balance
        self.username = username,
        self.chat_id = chat_id


class Chat(Entity):
    __tablename__ = 'chats'

    id = Column(psycopg2.sqltypes.BIGINT, primary_key=True)
    users = relationship("User", back_populates="chat")  # Обратная связь

    def __init__(self, id):
        self.id = id
