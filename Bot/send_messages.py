#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import telegram
from mensa import get_today_menus, get_all_user_and_mensas
from time import sleep
from token2 import token2


# todo: schedule this every day
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
        bot.send_message(chat_id=cid, text=text, parse_mode='HTML')
        sleep(0.05)  # avoiding flood limits

def get_mensa_text(mensa, menus_cpy):
    menus = menus_cpy.copy()
    for i in range(len(menus)):
        num = menus[i].find("&#x1F")
        if num != -1:
            symbols = menus[i][num:]
            menus[i] = menus[i][0:num-1]
            menus[i] = menus[i].replace(": ", " " + symbols + ":" + "\r\n", 1)

    return "<u><b>%s:</b></u>\n" % mensa +\
               "\n".join("\r\n<b>%s%s</b>%s" % m.partition(":") for m in menus)

if __name__ == '__main__':
    main()
