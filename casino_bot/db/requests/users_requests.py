import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.exc import NoResultFound, PendingRollbackError
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from casino_bot.db.entities import Entity
from casino_bot.db.entities.entities import User

host = os.getenv('HOST')
dbname = os.getenv('DB_NAME')
dbuser = os.getenv('DB_USERNAME')
dbpassw = os.getenv('DB_PASSWORD')

engine = create_engine(f'postgresql://{dbuser}:{dbpassw}@{host}/{dbname}')
Entity.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


def get_user(username):
    try:
        return session.get(User, username)
    except PendingRollbackError:
        logging.warning('rollback error')
        session.rollback()
        get_user(username)


def add_user(user):
    try:
        session.add(user)
    except PendingRollbackError:
        logging.warning('rollback error')
        session.rollback()
        add_user(user)
    session.commit()


def set_balance(user, balance):
    try:
        session.query(User).filter(User.id == user.id).update({User.balance: balance}, synchronize_session=False)
    except PendingRollbackError:
        logging.warning('rollback error')
        session.rollback()
        set_balance(user, balance)
    session.commit()
