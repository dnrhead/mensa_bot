#!/usr/bin/env python

import logging
import mensa
from telegram.ext import Application, CommandHandler
from send_messages import send_message_to_all
from datetime import datetime, timedelta
import sys
from config import Config
from utils import format_menus, format_date

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - '
                    '%(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


async def start(update, context):
    await update.message.reply_text('Hallo! Füge Mensen zu deiner Liste mit '
                                    'dem /add Befehl hinzu.\nJeden Tag um '
                                    'etwa 9 Uhr wird dir geschickt, was es '
                                    'zu essen gibt!'

                                    '\nFalls du Hilfe bei der Bedienung des '
                                    'Bots brauchst, schicke den /help Befehl.'
                                    '\n')

    print("start command sent", update.message.chat_id)


async def add(update, context):
    mensa_txt = " ".join(context.args)
    mensa_to_add = mensa.get_matching_mensa(mensa_txt, config.get_mensas())
    if mensa_to_add:
        db = config.get_database()
        db.add_mensa_subscription(update.message.chat_id, mensa_to_add)
        await update.message.reply_text('%s wurde der Liste hinzugefügt.' %
                                        mensa_to_add)
        print("Mensa added.")
    else:
        await update.message.reply_text('Keine passende Mensa "%s" gefunden'
                                        % mensa_txt)


async def remove(update, context):
    mensa_txt = " ".join(context.args)
    mensa_to_remove = mensa.get_matching_mensa(mensa_txt, config.get_mensas())
    if mensa_to_remove:
        config.get_database().remove_mensa_subscription(update.message.chat_id,
                                                        mensa_to_remove)
        await update.message.reply_text('%s wurde aus der Liste entfernt.' %
                                        mensa_to_remove)
    else:
        await update.message.reply_text('Keine passende Mensa "%s" gefunden'
                                        % mensa_txt)


async def remove_all(update, context):
    config.get_database().remove_mensa_subscriptions(update.message.chat_id)
    await update.message.reply_text('Alle abonnierten Mensen wurden entfernt.')


async def show_list(update, context):
    await update.message.reply_text('Du hast folgende Mensen abboniert:')
    db = config.get_database()
    mensas_sub = db.get_mensas_subscription(update.message.chat_id)
    formatted = mensa.format_mensa_list(mensas_sub, config.get_mensas())
    await update.message.reply_text(formatted)


async def week(update, context):
    today = datetime.today()
    db = config.get_database()
    menus = []
    for i in range(7):
        date = today + timedelta(i - today.weekday())
        # TODO: It is not necessary to fetch all menus here, only `subs` are
        # needed
        mensa_menus = mensa.fetch_all_menus(config, date)
        subs = db.get_mensas_subscription(update.message.chat_id)
        for m in subs:
            menus = mensa_menus[m]
            if not menus:
                continue
            menus.append(format_menus(m, menus, date))
    await update.message.reply_text("\n\n".join(menus), parse_mode='HTML')


async def essen(update, context, delta):
    date = datetime.today() + timedelta(delta)
    # TODO: It is not necessary to fetch all menus here, only `subs` are needed
    mensa_menus = mensa.fetch_all_menus(config, date)
    db = config.get_database()
    subs = db.get_mensas_subscription(update.message.chat_id)
    for m in subs:
        menus = mensa_menus[m]
        if not menus:
            msg = f"{format_date(date)} kein Essen in der {m}"
            await update.message.reply_text(msg, parse_mode='HTML')
            continue
        text = format_menus(m, menus, date)
        await update.message.reply_text(text, parse_mode='HTML')


def wochentag(weekday):
    async def f(update, context):
        delta = weekday - datetime.today().weekday()
        await essen(update, context, delta)
    return f


async def show_help(update, context):
    with open("help.html") as f:
        content = f.readlines()
    await update.message.reply_text(''.join(content) + mensa.format_mensa_list(
        config.get_mensas(), config.get_mensas()), parse_mode='HTML')


async def get_info(update, context):
    if update.message.chat_id in config.get_admin_ids():
        users_mensas = config.get_database().get_all_user_and_mensas()
        await update.message.reply_text("unique sending messages %d" %
                                        len(users_mensas))

        await update.message.reply_text("unique users %d" %
                                        len(set([i[0] for i in users_mensas])))
        await update.message.reply_text("unique mensas %d" %
                                        len(set([i[1] for i in users_mensas])))


async def announce(update, context):
    if update.message.chat_id in config.get_admin_ids():
        await send_message_to_all(context.bot, " ".join(context.args))


async def feedback(update, context):
    answer_r = "Feedback: \n"
    answer = " ".join(context.args)
    if answer.strip() != "":
        answer = answer_r + answer
        answer += "\n chat_id: " + str(update.message.chat_id)
        for i in config.get_admin_ids():
            await context.bot.send_message(chat_id=i, text=answer,
                                           parse_mode='HTML')
        await update.message.reply_text("Danke, dein Feedback wurde gesendet")


def overwrite_menus(update, context):
    if update.message.chat_id in config.get_admin_ids():
        mensa.overwrite_current_menus(config)


def main():
    """Run bot."""
    # Create the Application and pass it the token from the config.
    dp = Application.builder().token(config.get_token()).build()
    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add", add))
    dp.add_handler(CommandHandler("list", show_list))
    dp.add_handler(CommandHandler("remove", remove))
    dp.add_handler(CommandHandler("removeall", remove_all))
    dp.add_handler(CommandHandler("help", show_help))
    dp.add_handler(CommandHandler("feedback", feedback))

    dp.add_handler(CommandHandler("essen", lambda u, c: essen(u, c, 0)))
    dp.add_handler(CommandHandler("week", week))
    dp.add_handler(CommandHandler("heute", lambda u, c: essen(u, c, 0)))
    dp.add_handler(CommandHandler("morgen", lambda u, c: essen(u, c, 1)))
    weekdays = ["montag", "dienstag", "mittwoch", "donnerstag", "freitag",
                "samstag", "sonntag"]
    for i, w in enumerate(weekdays):
        dp.add_handler(CommandHandler(w, wochentag(i)))

    # Admin commands
    dp.add_handler(CommandHandler("get_info", get_info))
    dp.add_handler(CommandHandler("announce", announce))
    dp.add_handler(CommandHandler("overwrite", overwrite_menus))

    # Start the Bot
    dp.run_polling()
    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    print("should be started now")
    print("started bot")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <config.json>")
        sys.exit()
    global config
    config = Config(sys.argv[1])
    print("try to start bot")
    main()
