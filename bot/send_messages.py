#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import telegram
from telegram.error import NetworkError, Unauthorized
from mensa import *


# todo: schedule this every day
def main():
    """Run the bot."""
    global update_id
    # Telegram Bot Authorization Token
    bot = telegram.Bot("....")
    

    # get the first pending update_id, this is so we can skip over it in case
    # we get an "Unauthorized" exception.
    try:
        update_id = bot.get_updates()[0].update_id
    except IndexError:
        update_id = None

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # todo add check wether mensa is opened today
    mensa_essen = get_today_menus()
    data_to_send = get_all_user_and_mensas()
    # todo iterate over all, check "Avoiding flood limits"
    for pairs in data_to_send:
        text = pairs[1] + " "
        for es in mensa_essen[pairs[1]]:
            text = text + " " + es
        bot.send_message(chat_id=pairs[0], text=text)
    
if __name__ == '__main__':
    main()
    