#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import telegram
from mensa import fetch_all_menus
from time import sleep
import sys
from datetime import datetime
from config import Config
from utils import format_menus
import asyncio


async def send_menus(bot, config):
    """Run the bot."""
    date = datetime.today()
    mensa_menus = fetch_all_menus(config, date)
    users_mensas = config.get_database().get_all_user_and_mensas()
    print("Sending menus in %d messages" % (len(users_mensas)))
    for cid, mensa in users_mensas:
        menus = mensa_menus[mensa]
        if not menus:
            continue
        await send_message(bot, cid, format_menus(mensa, menus, date))


async def send_message_to_all(bot, users, msg):
    print("Sending message to all %d users" % len(users))
    for cid in users:
        await send_message(bot, cid, msg)


async def send_message(bot, chat_id, message):
    try:
        await bot.send_message(chat_id=chat_id, text=message,
                               parse_mode='HTML')
    except Exception as ex:
        print("Could not send message to", chat_id, str(ex))
    sleep(0.05)  # avoiding flood limits


async def main():
    if len(sys.argv) == 1:
        print(f"Usage: python3 {__file__} <config.json> [message to all]")
        sys.exit()
    config = Config(sys.argv[1])
    bot = telegram.Bot(config.get_token())
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - '
                        '%(message)s')
    async with bot:
        if len(sys.argv) > 2:
            await send_message_to_all(bot, config.get_database().get_users(),
                                      " ".join(sys.argv[2:]))
        else:
            await send_menus(bot, config)

if __name__ == '__main__':
    asyncio.run(main())
