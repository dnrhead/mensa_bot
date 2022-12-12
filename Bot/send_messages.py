#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import telegram
from db_tools import get_all_user_and_mensas, get_users
from mensa import fetch_all_menus, format_date
from time import sleep
import sys
from datetime import datetime
# Define your own token here
from token2 import token2


def initialiaze():
    
    # Telegram Bot Authorization Token
    bot = telegram.Bot(token2)

    # get the first pending update_id, this is so we can skip over it in case
    # we get an "Unauthorized" exception.
    try:
        update_id = bot.get_updates()[0].update_id
    except IndexError:
        update_id = None

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - '
                        '%(message)s')
    return bot


def send_menus(bot):
    """Run the bot."""
    date = format_date(datetime.today())
    mensa_menus = fetch_all_menus(date)
    users_mensas = get_all_user_and_mensas()
    print("Sending menus in %d messages" % (len(users_mensas)))
    for cid, mensa in users_mensas:
        menus = mensa_menus[mensa]
        if not menus:
            continue
        send_message(bot, cid, get_mensa_text(mensa, menus, date))


def send_message_to_all(bot, msg):
    users = get_users()
    print("Sending message to all %d users" % len(users))
    for cid in users:
        send_message(bot, cid, msg)


def send_message(bot, chat_id, message):
    try:
        bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
    except Exception as ex:
        print("Could not send message to", chat_id, str(ex))
    sleep(0.05)  # avoiding flood limits


def get_mensa_text(mensa, menus, date):
    res = "<u><b>%s (%s):</b></u>" % (mensa, date)
    for m in menus:
        num = m.find("&#x1F")
        symbols = "" if num == -1 else " " + m[num:]
        tmp = m if num == -1 else m[:num-1]
        res += "\n\n<b>" + tmp.replace(": ", symbols + ":</b>\n", 1)
    return res


if __name__ == '__main__':
    bot = initialiaze()
    if len(sys.argv) > 1:
        send_message_to_all(bot, " ".join(sys.argv[1:]))
    else:
        send_menus(bot)
