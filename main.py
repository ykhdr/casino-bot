import enum
import logging
import os
import time
import traceback
from contextlib import closing

from telebot import TeleBot
from telebot.types import Message

from casino_bot.db.entities.entities import User
from casino_bot.db.requests import engine
from casino_bot.db.requests.chat_requests import add_chat
from casino_bot.db.requests.users_requests import add_user, get_user, set_balance, get_user_by_username, add_balance

bot = TeleBot(os.getenv('BOT_TOKEN'))

START_BALANCE = 10000

active_users = []
users_balance = {}


class CasinoWinnings(enum.Enum):
    bar = 20
    grape = 30
    lemon = 40
    seven = 50
    nothing = 0


def combination(value):
    if value == 1:
        return CasinoWinnings.bar
    elif value == 22:
        return CasinoWinnings.grape
    elif value == 43:
        return CasinoWinnings.lemon
    elif value == 64:
        return CasinoWinnings.seven
    else:
        return CasinoWinnings.nothing


def register(user_id, username, message):
    chat_id = message.chat.id
    add_chat(chat_id)

    user = User(id=user_id, username=username, balance=START_BALANCE, chat_id=chat_id)
    add_user(user)

    bot.reply_to(message, f'Ты авторизировался, хрш. Твой баланс: {START_BALANCE}.\nТеперь можешь делать ставки')


@bot.message_handler(chat_types=['group', 'supergroup'], commands=['bet'])
def handle_bet_cmd(message: Message):
    chat_id = message.chat.id
    params = message.text.split()[1:]

    username = message.from_user.username
    user_id = message.from_user.id

    user = get_user(user_id)

    if not user:
        register(user_id, username, message)
        return

    if not params:
        bot.reply_to(message, 'Введите сумму для ставки. Пример: /bet 777')
        return

    bet_s = params[0]

    if not bet_s.isdigit() or int(bet_s) <= 0:
        bot.reply_to(message, 'Ставка должна быть неотрицательным числом')
        return

    bet = int(bet_s)

    user_balance = user.balance

    if user_balance < bet:
        bot.reply_to(message,
                     f'Чел, балансик то твой нулевый: {user_balance}. Подкопи-ка златых или делай ставку поменьше')
        return

    ans = bot.send_dice(chat_id, '🎰')
    value = int(ans.json['dice']['value'])

    user_balance -= bet
    cw = combination(value)

    set_balance(user, user_balance)
    if cw == CasinoWinnings.nothing:
        time.sleep(1.5)
        bot.reply_to(message, f'Упс.. Ты проиграл. Теперь твой баланс: {user_balance}')
    else:
        gain = bet * cw.value
        add_balance(user_id, gain)
        user = get_user(user_id)
        time.sleep(1.5)
        bot.reply_to(message, f'Поздравляю! Ты выиграл: {gain}. Теперь твой баланс: {user.balance}')


@bot.message_handler(chat_types=['group', 'supergroup'], commands=['balance'])
def handle_balance_cmd(message: Message):
    username = message.from_user.username
    user_id = message.from_user.id

    user = get_user(user_id)

    if not user:
        register(user_id, username, message)
        return

    bot.reply_to(message, f'Твой баланс: {user.balance}')


@bot.message_handler(chat_types=['group', 'supergroup'], commands=['donate'])
def handle_donate_cmd(message: Message):
    username_from = message.from_user.username
    user_id_from = message.from_user.id

    user_from = get_user(user_id_from)

    if not user_from:
        register(user_id_from, username_from, message)
        return

    params = message.text.split()[1:]

    if len(params) < 2:
        bot.reply_to(message, 'Укажи ник и сумму которую хочешь закинуть на додеп молодому: /donate username 777')
        return

    username_to = params[0]

    user_to = get_user_by_username(username_to)

    if not user_to:
        bot.reply_to(message, 'Пользователя с таким ником не существует')
        return

    if user_from.id == user_to.id:
        bot.reply_to(message, 'Переводы себе бессмысленны')
        return

    if not params[1].isdigit() or int(params[1]) <= 0:
        bot.reply_to(message, 'Сумма для перевода должна быть положительным числом')
        return

    dep = int(params[1])

    if dep > user_from.balance:
        bot.reply_to(message, f'Малыш, не дорос ты еще до таких сумм. Твой баланс: {user_from.balance}')
        return

    new_balance_from = user_from.balance - dep
    new_balance_to = user_to.balance + dep

    set_balance(user_from, new_balance_from)
    set_balance(user_to, new_balance_to)

    bot.reply_to(message,
                 f'Поздравляю, ты дал {username_to} возможность еще раз потратить свое баблишко. Твой баланс: {new_balance_from}')


@bot.message_handler(chat_types=['private'], commands=['topup'],
                     func=lambda message: message.from_user.username == os.getenv('ADMIN_USERNAME'))
def top_up_balance(message: Message):
    chat_id = message.chat.id
    params = message.text.split()[1:]

    if len(params) < 2:
        bot.send_message(chat_id, 'Укажи ник и скольку человек нужно закинуть на счет')
        return

    username = params[0]

    user = get_user_by_username(username)

    if not user:
        bot.send_message(chat_id, 'Такого пользователя нет')
        return

    if not params[1].isdigit():
        bot.send_message(chat_id, 'Укажите баланс числом > 0')

    adding = int(params[1])

    set_balance(user, user.balance + adding)

    bot.send_message(chat_id,
                     f'Баланс пользователя {username} увеличен на {adding}. Текущий баланс: {user.balance}')


def migrate_schema():
    try:
        with engine.connect() as conn:
            with closing(conn.connection) as connection:
                cursor = connection.cursor()

                with open("db/db_init.sql", 'r') as f:
                    migration_script = f.read()
                    cursor.execute(migration_script)
                    connection.commit()
        return True
    except:
        logging.warning('Ошибка при миграции схемы базы данных')
        traceback.print_exc()
        return False


def main():
    if not migrate_schema():
        exit(1)
    bot.infinity_polling()


if __name__ == "__main__":
    main()
