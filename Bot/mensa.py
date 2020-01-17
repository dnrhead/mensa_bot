from urllib.request import urlopen
import re
import sqlite3
from datetime import datetime

mensas = ['Mensa Rempartstrasse', 'Mensa Institutsviertel',
          'Mensa Littenweiler', 'Mensa Flugplatz', 'Mensa Furtwangen',
          'Mensa Offenburg', 'Mensa Gengenbach', 'Mensa Kehl',
          'Mensa Schwenningen', 'Mensa Trossingen',
          'Ausgabestelle EH Freiburg', 'MusiKantine', 'OHG Furtwangen']

DB_NAME = "database.db"


def retrieve_menus(mensa):
    with urlopen("https://www.swfr.de/essen-trinken/speiseplaene/"
                 + mensa.lower().replace(" ", "-")) as url:
        txt = url.read().decode()
    result = {}
    for i in txt.replace("<br>", ", ").split("<h3>"):
        split = i.split("</h3>")
        if len(split) != 2:
            continue
        day2, rest = split
        menus = re.findall(r'<h4.*?>(.*?)</h4><div.*?>\s*(.*?)<', rest)
        if menus:
            day = day2.split(" ")[1]
            result[day] = [t + ": " + f.strip(", ")
                           for t, f in menus if f.strip(", ")]
    return result


def get_today_menus():
    today = datetime.today()
    date = "%02d.%02d." % (today.day, today.month)
    result = {}
    for m in get_all_mensa_subscriptions():
        menus = get_menus(m, date)
        if menus == []:
            data = retrieve_menus(m)
            add_menus(m, data)
            if date in data:
                menus = data[date]
        result[m] = menus
    return result


def execute_sql(cmd):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute(cmd)
    result = cursor.fetchall()
    connection.commit()
    connection.close()
    return result


def initialize_database():
    execute_sql("CREATE TABLE IF NOT EXISTS users "
                "(user VARCHAR(30), mensa VARCHAR(30));")
    execute_sql("CREATE TABLE IF NOT EXISTS menus "
                "(mensa VARCHAR(30), date VARCHAR(30), menu VARCHAR(200));")


def add_mensa_subscription(user, mensa):
    execute_sql("INSERT INTO users VALUES (%r, %r);" % (user, mensa))


def remove_mensa_subscription(user, mensa):
    execute_sql("DELETE FROM users WHERE user=%r AND mensa=%r" %
                (user, mensa))


def get_mensas_subscription(user):
    return [i[0] for i in execute_sql("SELECT DISTINCT mensa FROM users WHERE "
                                      "user=%r" % user)]


def get_all_mensa_subscriptions():
    return [i[0] for i in execute_sql("SELECT DISTINCT mensa FROM users")]


def get_all_user_and_mensas():
    return execute_sql("SELECT DISTINCT * FROM users")


def get_menus(mensa, date):
    return [i[0] for i in execute_sql("SELECT DISTINCT menu FROM menus "
                                      "WHERE mensa=%r AND date=%r" %
                                      (mensa, date))]


def add_menus(mensa, data):
    values = ("(%r, %r, %r)" % (mensa, d, f) for d in data for f in data[d])
    execute_sql("INSERT INTO menus VALUES %s;" % ", ".join(values))
