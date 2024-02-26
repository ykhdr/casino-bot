from casino_bot.db.entities.entities import Chat
from casino_bot.db.requests import session


def add_chat(chat_id):
    try:
        session.begin()
        chat = session.query(Chat).filter(Chat.id == chat_id).first()
        if not chat:
            chat = Chat(id=chat_id)
            session.add(chat)
            session.commit()
        session.close()
        return chat
    except:
        session.rollback()
        raise
    finally:
        session.close()
