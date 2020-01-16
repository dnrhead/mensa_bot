from urllib.request import urlopen
import re
import os
import sqlite3

mensas = ['Mensa Rempartstrasse', 'Mensa Institutsviertel',
          'Mensa Littenweiler', 'Mensa Flugplatz', 'Mensa Furtwangen',
          'Mensa Offenburg', 'Mensa Gengenbach', 'Mensa Kehl',
          'Mensa Schwenningen', 'Mensa Trossingen',
          'Ausgabestelle EH Freiburg', 'MusiKantine', 'OHG Furtwangen']

DB_NAME = "users.db"

def get_data(mensa):
    assert mensa in mensas
    mensa_transformed = mensa.lower().replace(" ", "-")
    with urlopen("https://www.swfr.de/essen-trinken/speiseplaene/"
                 + mensa_transformed) as url:
        txt = url.read().decode()
    result = {}
    for i in txt.replace("<br>", " ").split("<h3>"):
        split = i.split("</h3>")
        if len(split) != 2:
            continue
        day2, rest = split
        day = day2.split(" ")[1]
        menus = re.findall(r'<h4.*?>(.*?)</h4><div.*?>\s*(.*?)<', rest)
        if menus:
            result[day] = [(t, f.strip()) for t, f in menus]
    return result


def initialize_database():
    if os.path.exists(DB_NAME):
        return
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE users (user VARCHAR(30), mensa VARCHAR(30));")
    connection.commit()
    connection.close()


def add_mensa(user, mensa):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO users VALUES (%r, %r);" % (user, mensa))
    connection.commit()
    connection.close()


def get_mensas(user):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT mensa FROM users WHERE user=%r" % user) 
    result = cursor.fetchall()
    connection.close()
    return result
