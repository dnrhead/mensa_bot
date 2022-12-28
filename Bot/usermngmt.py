#!/usr/bin/env python

import logging
import mensa
from telegram.ext import Updater, CommandHandler
from send_messages import send_message_to_all
from datetime import datetime, timedelta
import sys
from config import Config
from database import get_mensa_text

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - '
                    '%(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


def start(update, context):
    update.message.reply_text('Hallo! Füge Mensen zu deiner Liste mit dem '
                              '/add Befehl hinzu.\nJeden Tag um etwa 9 Uhr '
                              'wird dir geschickt, was es zu essen gibt!'

                              '\nFalls du Hilfe bei der Bedienung des Bots '
                              'brauchst, schicke den /help Befehl.\n')

    print("start command sent", update.message.chat_id)


def add(update, context):
    mensa_txt = " ".join(context.args)
    mensa_to_add = mensa.get_matching_mensa(mensa_txt)
    if mensa_to_add:
        db = config.get_database()
        db.add_mensa_subscription(update.message.chat_id, mensa_to_add)
        update.message.reply_text('%s wurde der Liste hinzugefügt.' %
                                  mensa_to_add)
        print("Mensa added.")
    else:
        update.message.reply_text('Keine passende Mensa "%s" gefunden'
                                  % mensa_txt)


def remove(update, context):
    mensa_txt = " ".join(context.args)
    mensa_to_remove = mensa.get_matching_mensa(mensa_txt)
    if mensa_to_remove:
        config.get_database().remove_mensa_subscription(update.message.chat_id,
                                                        mensa_to_remove)
        update.message.reply_text('%s wurde aus der Liste entfernt.' %
                                  mensa_to_remove)
    else:
        update.message.reply_text('Keine passende Mensa "%s" gefunden'
                                  % mensa_txt)


def remove_all(update, context):
    config.get_database().remove_mensa_subscriptions(update.message.chat_id)
    update.message.reply_text('Alle abonnierten Mensen wurden entfernt.')


def show_list(update, context):
    update.message.reply_text('Du hast folgende Mensen abboniert:')
    db = config.get_database()
    mensas_sub = db.get_mensas_subscription(update.message.chat_id)
    update.message.reply_text(mensa.format_mensa_list(mensas_sub))


def essen(update, context, delta):
    date = datetime.today() + timedelta(delta)
    mensa_menus = mensa.fetch_all_menus(config, date)
    db = config.get_database()
    subs = db.get_mensas_subscription(update.message.chat_id)
    for m in subs:
        menus = mensa_menus[m]
        if not menus:
            update.message.reply_text("%s kein Essen in der %s" %
                                      (date, m), parse_mode='HTML')
            continue
        text = get_mensa_text(m, menus, date)
        update.message.reply_text(text, parse_mode='HTML')


def wochentag(weekday):
    def f(update, context):
        delta = weekday - datetime.today().weekday()
        essen(update, context, delta)
    return f


def show_help(update, context):
    with open("help.html") as f:
        content = f.readlines()
    update.message.reply_text(''.join(content) + mensa.format_mensa_list(),
                              parse_mode='HTML')


def get_info(update, context):
    if update.message.chat_id in config.get_admin_ids():
        users_mensas = config.get_database().get_all_user_and_mensas()
        update.message.reply_text("unique sending messages %d" %
                                  len(users_mensas))

        update.message.reply_text("unique users %d" %
                                  len(set([i[0] for i in users_mensas])))
        update.message.reply_text("unique mensas %d" %
                                  len(set([i[1] for i in users_mensas])))


def announce(update, context):
    if update.message.chat_id in config.get_admin_ids():
        send_message_to_all(context.bot, " ".join(context.args))


def feedback(update, context):
    answer_r = "Feedback: \n"
    answer = " ".join(context.args)
    if answer.strip() != "":
        answer = answer_r + answer
        answer += "\n chat_id: " + str(update.message.chat_id)
        update.message.reply_text("Danke, dein Feedback wurde gesendet")
        for i in config.get_admin_ids():
            context.bot.send_message(chat_id=i, text=answer, parse_mode='HTML')


def main():
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(config.get_token(), use_context=True)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add", add))
    dp.add_handler(CommandHandler("list", show_list))
    dp.add_handler(CommandHandler("remove", remove))
    dp.add_handler(CommandHandler("removeall", remove_all))
    dp.add_handler(CommandHandler("help", show_help))
    dp.add_handler(CommandHandler("essen", lambda u, c: essen(u, c, 0)))
    dp.add_handler(CommandHandler("feedback", feedback))
    dp.add_handler(CommandHandler("get_info", get_info))
    dp.add_handler(CommandHandler("announce", announce))
    dp.add_handler(CommandHandler("overwrite", lambda u, c:
                                  mensa.overwrite_current_menus(config)))

    dp.add_handler(CommandHandler("morgen", lambda u, c: essen(u, c, 1)))
    weekdays = ["montag", "dienstag", "mittwoch", "donnerstag", "freitag",
                "samstag", "sonntag"]
    for i, w in enumerate(weekdays):
        dp.add_handler(CommandHandler(w, wochentag(i)))
    # Start the Bot
    updater.start_polling()
    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    print("should be started now")
    updater.idle()
    print("started bot")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <config.json>")
        sys.exit()
    global config
    config = Config(sys.argv[1])
    print("try to start bot")
    main()
