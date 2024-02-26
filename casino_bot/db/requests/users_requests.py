from casino_bot.db.entities.entities import User
from casino_bot.db.requests import session


def get_user(user_id):
    try:
        session.begin()
        user = session.get(User, user_id)
        return user
    except:
        session.rollback()
        raise
    finally:
        session.close()


def get_user_by_username(username):
    try:
        session.begin()
        user = session.query(User).filter(User.username == username).first()
        return user
    except:
        session.rollback()
        raise
    finally:
        session.close()


def add_user(user):
    try:
        session.begin()
        session.add(user)
        session.commit()
    except :
        session.rollback()
        raise
    finally:
        session.close()


def set_balance(user, balance):
    try:
        session.begin()
        session.query(User).filter(User.id == user.id).update({User.balance: balance}, synchronize_session=False)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def add_balance(user_id, gain):
    try:
        session.begin()
        user_balance = session.get(User, user_id).balance
        session.query(User).filter(User.id == user_id).update({User.balance: user_balance + gain})
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
