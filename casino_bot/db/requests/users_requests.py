import os

from sqlalchemy import create_engine
from sqlalchemy.exc import NoResultFound
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
        return session.get_one(User, username)
    except NoResultFound:
        return None


def add_user(user):
    session.add(user)
    session.commit()


def set_balance(user, balance):
    session.query(User).filter(User.id == user.id).update({User.balance: balance}, synchronize_session=False)
    session.commit()
