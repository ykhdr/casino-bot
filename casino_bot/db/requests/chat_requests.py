from casino_bot.db.entities.entities import Chat
from casino_bot.db.requests import session


def add_chat(chat):
    if not session.get(Chat, chat):
        session.add(Chat, chat)
        session.commit()
        session.flush()
