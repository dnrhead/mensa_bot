#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import telegram
from mensa import get_today_menus, get_all_user_and_mensas
from time import sleep


# todo: schedule this every day
def main():
    """Run the bot."""
    global update_id
    # Telegram Bot Authorization Token
    bot = telegram.Bot("...")

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
        text = "<u><b>%s:</b></u>\n" % mensa +\
               "\n".join("<b>" + m.replace(":", ":</b>") for m in menus)
        bot.send_message(chat_id=cid, text=text, parse_mode='HTML')
        sleep(0.05)  # avoiding flood limits


if __name__ == '__main__':
    main()
