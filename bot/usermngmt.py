#!/usr/bin/env python

from urllib.request import urlopen
import re
import logging
from mensa import *

from telegram.ext import Updater, CommandHandler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def start(update, context):
    update.message.reply_text('Hallo! Füge Mensen zu deiner List mit dem /add Befehl hinzu, jeden Tag um etwa 10 Uhr wird dir gesagt, was es zu Essen gibt!')

def add(update, context):
    mensa_to_add = ""
    for i in range(len(context.args)):
        mensa_to_add = context.args[i] + " "
    mensa_to_add = mensa_to_add[0:-1]
    if mensa_to_add in mensas:
        add_mensa_subscription(update.message.chat_id, mensa_to_add)
        update.message.reply_text('%s wurde der Liste hinzugefügt.' % mensa_to_add)
    else:
        update.message.reply_text('Konnte nicht hinzugefügt werden. Versuche es erneut.')


def remove(update, context):
    mensa_to_remove = ""
    for i in range(len(context.args)):
        mensa_to_remove = context.args[i] + " "
    mensa_to_remove = mensa_to_remove[0:-1]
    if mensa_to_remove in mensas:
        remove_mensa_subscription(update.message.chat_id, mensa_to_remove)
        update.message.reply_text('%s wurde aus der Liste entfernt.' % mensa_to_remove)
    else:
        update.message.reply_text('Konnte nicht entfernt werden. Versuche es erneut. Oder nutze \removeAll')

def removeAll(update, context):
    print("todo")

def show_list(update, context):
    mensas_sub = get_mensas_subscription(update.message.chat_id)
    update.message.reply_text('Du hast folgende Mensen abboniert:')
    for mensa in mensas_sub:
        update.message.reply_text(mensa)

def main():
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("...", use_context=True)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add", add))
    dp.add_handler(CommandHandler("list", show_list))
    dp.add_handler(CommandHandler("remove", remove))
    dp.add_handler(CommandHandler("removeAll", removeAll))
    # Start the Bot
    updater.start_polling()
    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    initialize_database()
    print("should be started now")
    updater.idle()
    print("started bot")

if __name__ == '__main__':
    print("try to start bot")
    main()
