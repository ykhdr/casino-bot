import enum
import os
import time

import sqlalchemy
from requests import session
from sqlalchemy import create_engine

from telebot import TeleBot
from telebot.types import Message

from casino_bot.db.entities.entities import User
from casino_bot.db.requests.users_requests import add_user, get_user, set_balance

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


@bot.message_handler(chat_types=['group', 'supergroup'], commands=['bet'])
def handle_bet_cmd(message: Message):
    chat_id = message.chat.id
    params = message.text.split()[1:]

    username = message.from_user.username

    user = get_user(username)

    if not user:
        user = User(username, START_BALANCE)
        add_user(user)

        # active_users.append(username)
        # users_balance[username] = START_BALANCE
        bot.reply_to(message, f'Ты авторизировался, хрш. Твой баланс: {START_BALANCE}.\nТеперь можешь делать ставки')
        return

    if not params:
        bot.send_message(chat_id, 'Введите сумму для ставки. Пример: /bet 777')
        return

    bet_s = params[0]

    if not bet_s.isdigit() or int(bet_s) <= 0:
        bot.send_message(chat_id, 'Ставка должна быть неотрицательным числом')
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

    if cw == CasinoWinnings.nothing:
        set_balance(user, user_balance)
        # users_balance[username] = user_balance
        time.sleep(1.5)
        bot.reply_to(message, f'Упс.. Ты проиграл. Теперь твой баланс: {user_balance}')
    else:
        gain = bet * cw.value
        user_balance += gain
        set_balance(user, user_balance)
        # users_balance[username] = user_balance
        time.sleep(1.5)
        bot.reply_to(message, f'Поздравляю! Ты выиграл: {gain}. Теперь твой баланс: {user_balance}')


@bot.message_handler(chat_types=['group', 'supergroup'], commands=['balance'])
def handle_balance_cmd(message: Message):
    chat_id = message.chat.id
    username = message.from_user.username

    user = get_user(username)

    if not user:
        user = User(username, START_BALANCE)
        add_user(user)
        # active_users.append(username)
        # users_balance[username] = START_BALANCE
        bot.reply_to(message, f'Ты авторизировался, хрш. Твой баланс: {START_BALANCE}.\nТеперь можешь делать ставки')
        return

    # user_balance = users_balance[username]
    # bot.reply_to(message, f'Твой баланс: {user_balance}')
    bot.reply_to(message, f'Твой баланс: {user.balance}')


@bot.message_handler(chat_types=['private'], commands=['topup'],
                     func=lambda message: message.from_user.username == 'rdhkyy')
def top_up_balance(message: Message):
    chat_id = message.chat.id
    params = message.text.split()[1:]

    if len(params) < 2:
        bot.send_message(chat_id, 'Укажи ник и скольку человек нужно закинуть на счет')
        return

    username = params[0]

    user = get_user(username)

    if not user:
        bot.send_message(chat_id, 'Такого пользователя нет')
        return

    if not params[1].isdigit():
        bot.send_message(chat_id, 'Укажите баланс числом > 0')

    adding = int(params[1])

    # users_balance[username] = users_balance[username] + adding
    set_balance(user, user.balance + adding)

    bot.send_message(chat_id,
                     f'Баланс пользователя {username} увеличен на {adding}. Текущий баланс: {user.balance}')


bot.infinity_polling()
