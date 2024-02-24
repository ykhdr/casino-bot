import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.exc import NoResultFound, PendingRollbackError
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from casino_bot.db.entities import Entity
from casino_bot.db.entities.entities import User
from casino_bot.db.requests import session


def get_user(user_id):
    try:
        return session.get(User, user_id)
    except PendingRollbackError:
        logging.warning('rollback error')
        session.rollback()
        get_user(user_id)


def get_user_by_username(username):
    return session.query(User).filter(User.username == username).first()


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
