import sqlite3
import os
import re

DB_NAME = "database.db"
EXCLUDE_WORDS = ["essen", "oder", "wahl", "schneller", "teller", "pavillon",
                 "spezialitäten", "außerdem", "buffet", "auswahl", "wunsch",
                 "bunter", "geriebener", "gebackenes"]


def execute_sql(cmd):
    dirname = os.path.dirname(os.path.abspath(__file__))
    dbpath = os.path.join(dirname, DB_NAME)
    connection = sqlite3.connect(dbpath)
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


def remove_mensa_subscriptions(user):
    execute_sql("DELETE FROM users WHERE user=%r" % user)


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
    values = []
    for d in data:
        if data[d]:
            values.extend("(%r, %r, %r)" % (mensa, d, f) for f in data[d])
        else:
            values.append("(%r, %r, NULL)" % (mensa, d))
    execute_sql("INSERT INTO menus VALUES %s;" % ", ".join(values))


def remove_menus(mensa, date):
    execute_sql("DELETE FROM menus WHERE mensa=%r AND date=%r" % (mensa, date))


def get_food_counts(mensa):
    menus = execute_sql("SELECT DISTINCT menu FROM menus WHERE mensa=%r" %
                        mensa)
    d = {}
    for m, in menus:
        if not m:
            continue
        words = re.findall(r'(\w+)', m)
        for w in words:
            if w.islower() or len(w) < 4 or w.lower() in EXCLUDE_WORDS:
                continue
            d[w] = d.get(w, 0) + 1
    return sorted(d.items(), key=lambda x: -x[1])
