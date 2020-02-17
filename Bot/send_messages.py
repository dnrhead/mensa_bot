#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import telegram
from db_tools import get_all_user_and_mensas
from mensa import get_today_menus
from time import sleep
# Define your own token here
from token2 import token2


def main():
    """Run the bot."""
    global update_id
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

    mensa_menus = get_today_menus()
    users_mensas = get_all_user_and_mensas()
    print("Sending %d messages" % (len(users_mensas)))
    for cid, mensa in users_mensas:
        menus = mensa_menus[mensa]
        if not menus:
            continue
        text = get_mensa_text(mensa, menus)
        try:
            bot.send_message(chat_id=cid, text=text, parse_mode='HTML')
        except:
            print("could not send message")
        sleep(0.05)  # avoiding flood limits


def get_mensa_text(mensa, menus):
    res = "<u><b>%s:</b></u>" % mensa
    for m in menus:
        num = m.find("&#x1F")
        symbols = "" if num == -1 else " " + m[num:]
        tmp = m if num == -1 else m[:num-1]
        res += "\n\n<b>" + tmp.replace(": ", symbols + ":</b>\n", 1)
    return res


if __name__ == '__main__':
    main()
