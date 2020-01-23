#!/usr/bin/env python

import logging
from mensa import *
from telegram.ext import Updater, CommandHandler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - '
                    '%(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


def start(update, context):
    update.message.reply_text('Hallo! Füge Mensen zu deiner Liste mit dem '
                              '/add Befehl hinzu.\nJeden Tag um etwa 9 Uhr '
                              'wird dir geschick, was es zu Essen gibt!'
                              '\nFalls du Hilfe bei der Bedienung des Bots '
                              'brauchst, schicke den /help Befehl.\n')
    print("start command sent")


def add(update, context):
    mensa_to_add = get_matching_mensa(" ".join(context.args))
    if mensa_to_add:
        add_mensa_subscription(update.message.chat_id, mensa_to_add)
        update.message.reply_text('%s wurde der Liste hinzugefügt.' %
                                  mensa_to_add)
        print("Mensa added.")
    else:
        update.message.reply_text('Konnte nicht hinzugefügt werden. Versuche '
                                  'es erneut.')


def remove(update, context):
    mensa_to_remove = get_matching_mensa(" ".join(context.args))
    if mensa_to_remove:
        remove_mensa_subscription(update.message.chat_id, mensa_to_remove)
        update.message.reply_text('%s wurde aus der Liste entfernt.' %
                                  mensa_to_remove)
    else:
        update.message.reply_text('Konnte nicht entfernt werden. Versuche es '
                                  'erneut. Oder nutze \removeAll')


def remove_all(update, context):
    remove_mensa_subscriptions(update.message.chat_id)
    update.message.reply_text('Alle abonnierten Mensen wurden entfernt.')


def show_list(update, context):
    mensas_sub = get_mensas_subscription(update.message.chat_id)
    update.message.reply_text('Du hast folgende Mensen abboniert:')
    for mensa in mensas_sub:
        update.message.reply_text(mensa)

def essen(update, context):
    mensa_menus = get_today_menus()
    subs = get_mensas_subscription(update.message.chat_id)
    for mensa in subs:
        menus = mensa_menus[mensa]
        if not menus:
            update.message.reply_text("Heute kein Essen in der %s" % mensa, parse_mode='HTML')
            continue
        text = "<u><b>%s:</b></u>\n" % mensa +\
               "\n".join("<b>%s%s</b>%s" % m.partition(":") for m in menus)
        update.message.reply_text(text, parse_mode='HTML')

def show_help(update, context):
    with open("help.html") as f:
        content = f.readlines()
    update.message.reply_text(''.join(content), parse_mode='HTML')

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
    dp.add_handler(CommandHandler("removeall", remove_all))
    dp.add_handler(CommandHandler("help", show_help))
    dp.add_handler(CommandHandler("essen", essen))
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
