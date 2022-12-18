#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import telegram
from mensa import fetch_all_menus
from time import sleep
import sys
from datetime import datetime
from config import Config
from database import format_date


def send_menus(bot, config):
    """Run the bot."""
    date = datetime.today()
    mensa_menus = fetch_all_menus(config, date)
    users_mensas = config.get_database().get_all_user_and_mensas()
    print("Sending menus in %d messages" % (len(users_mensas)))
    for cid, mensa in users_mensas:
        menus = mensa_menus[mensa]
        if not menus:
            continue
        send_message(bot, cid, get_mensa_text(mensa, menus, date))


def send_message_to_all(bot, users, msg):
    print("Sending message to all %d users" % len(users))
    for cid in users:
        send_message(bot, cid, msg)


def send_message(bot, chat_id, message):
    try:
        bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
    except Exception as ex:
        print("Could not send message to", chat_id, str(ex))
    sleep(0.05)  # avoiding flood limits


# TODO: This method should be moved to a utils class (along with format_date?)
def get_mensa_text(mensa, menus, date):
    res = "<u><b>%s (%s):</b></u>" % (mensa, format_date(date))
    for m in menus:
        num = m.find("&#x1F")
        symbols = "" if num == -1 else " " + m[num:]
        tmp = m if num == -1 else m[:num-1]
        res += "\n\n<b>" + tmp.replace(": ", symbols + ":</b>\n", 1)
    return res


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print(f"Usage: python3 {__file__} <config.json> [message to all]")
        sys.exit()
    config = Config(sys.argv[1])
    bot = telegram.Bot(config.get_token())
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - '
                        '%(message)s')
    if len(sys.argv) > 2:
        send_message_to_all(bot, config.get_database().get_users(),
                            " ".join(sys.argv[2:]))
    else:
        send_menus(bot, config)
