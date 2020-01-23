from urllib.request import urlopen
import re
import sqlite3
from datetime import datetime

swfr_mensas = ['Mensa Rempartstrasse', 'Mensa Institutsviertel',
               'Mensa Littenweiler', 'Mensa Flugplatz', 'Mensa Furtwangen',
               'Mensa Offenburg', 'Mensa Gengenbach', 'Mensa Kehl',
               'Mensa Schwenningen', 'Mensa Trossingen', 'Mensa Loerrach',
               'Ausgabestelle EH Freiburg', 'MusiKantine', 'OHG Furtwangen']
mensas = swfr_mensas + ["Solarcasino"]

DB_NAME = "database.db" # while sheduled with cron, use absoult path


def retrieve_menus(mensa):
    if mensa in swfr_mensas:
        return retrieve_menus_swfr(mensa)
    if mensa == "Solarcasino":
        return retrieve_menus_solarcasino()
    raise NotImplementedError("Unhandled case: %r" % mensa)


def retrieve_menus_swfr(mensa):
    with urlopen("https://www.swfr.de/essen-trinken/speiseplaene/"
                 + mensa.lower().replace(" ", "-")) as url:
        txt = url.read().decode()
    result = {}
    for i in txt.replace("<br>", ", ").split("<h3>"):
        m = re.search(r'(\d+\.\d+\.).*?</h3>(.*)', i, re.DOTALL)
        if not m:
            continue
        menus = re.findall(r'<h4.*?>(.*?)</h4><div.*?>\s*(.*?)<', m.group(2))
        result[m.group(1)] = [t + ": " + f.strip(", ")
                              for t, f in menus if f.strip(", ")]
    # Sundays do not occur on the site, therefore add [] manually
    result[get_next_weekday(6)] = []
    return result


def retrieve_menus_solarcasino():
    with urlopen("https://kantine.ise.fhg.de/sic/") as url:
        txt = url.read().decode()
    result = {}
    menus = re.findall(r'<td class="(\d\d.\d\d.)\d+-.*?(\d)".*?>\s*'
                       r'(.*?)\s*</td>', txt)
    for date, n, f in menus:
        if date not in result:
            result[date] = []
        food_tmp = re.sub(r'\s*<sup>(.*?)</sup>\s*', " ", f)
        food = re.sub(r'\s*&#.*', "", food_tmp)
        if food == "-":
            continue
        result[date].append("Essen %s: %s" % (n, food))
    # Saturndays and sundays do not occur on the site, so add [] manually
    result[get_next_weekday(5)] = []
    result[get_next_weekday(6)] = []
    return result


def get_next_weekday(day):
    today = datetime.today()
    return "%02d.%02d." % (today.day + day - today.weekday(), today.month)


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
        result[m] = list(filter(bool, menus))
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


def edit_distance(s1, s2):
    if len(s1) < len(s2):
        return edit_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def get_matching_mensa(mensa):
    min_ed = 3
    res = None
    for m in mensas:
        for m2 in (m.lower(), m.lower().replace("mensa", "").strip()):
            ed = edit_distance(m2, mensa.lower())
            if ed == 0:
                return m
            if ed < min_ed:
                min_ed = ed
                res = m
    return res
