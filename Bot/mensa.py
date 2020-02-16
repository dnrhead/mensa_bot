from urllib.request import urlopen
import re
from datetime import datetime, timedelta
from db_tools import *

swfr_mensas = ['Mensa Rempartstrasse', 'Mensa Institutsviertel',
               'Mensa Littenweiler', 'Mensa Flugplatz', 'Mensa Furtwangen',
               'Mensa Offenburg', 'Mensa Gengenbach', 'Mensa Kehl',
               'Mensa Schwenningen', 'Mensa Trossingen', 'Mensa Loerrach',
               'Ausgabestelle EH Freiburg', 'MusiKantine', 'OHG Furtwangen']
mensas = swfr_mensas + ["Solarcasino"]

DB_NAME = "database.db"


def retrieve_menus(mensa):
    if mensa in swfr_mensas:
        return retrieve_menus_swfr(mensa)
    if mensa == "Solarcasino":
        return retrieve_menus_solarcasino()
    raise NotImplementedError("Unhandled case: %r" % mensa)


def format_swfr_menu(menu):
    v, t, f, i = menu

    def matches(*args):
        return any(x in f.lower() for x in args)
    res = t + ": " + f.strip(", ").replace(":,", ":")
    if "veg" in v or matches(" veg"):
        res += " &#x1F331"
    if matches("hähn", "huhn", "hühn", "pute", "flügel"):
        res += " &#x1F414"
    if matches("lamm"):
        res += " &#x1F411"
    is_fish = matches("fisch", "pangasius", "lachs", "forelle", "meeres")
    if "Zusatzstoffe:" not in i:
        if is_fish:
            res += " &#x1F41F"
        return res
    i2 = i[i.index(":"):]
    if "sch" in i2:
        res += " &#x1F416"
    if "ri" in i2:
        res += " &#x1F404"
    if "nF" in i2 or is_fish:
        res += " &#x1F41F"
    return res


def retrieve_menus_swfr(mensa):
    assert mensa in swfr_mensas
    with urlopen("https://www.swfr.de/essen-trinken/speiseplaene/"
                 + mensa.lower().replace(" ", "-")) as url:
        txt = url.read().decode()
    result = {}
    for i in txt.replace("<br>", ", ").split("<h3>"):
        m = re.search(r'(\d+\.\d+\.).*?</h3>(.*)', i, re.DOTALL)
        if not m:
            continue
        menus = re.findall(r'<div class="row (.*?) mb-2"><h4.*?>(.*?)</h4>'
                           r'<div.*?>\s*(.*?)<.*?>(.*?)<', m.group(2))
        result[m.group(1)] = list(map(format_swfr_menu, menus))
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
        food_tmp = re.sub(r'<sup>(.*?)(?:</sup>|\))', "", f)
        food = re.sub(r'\s+', " ", food_tmp)
        if food == "-":
            continue
        if date not in result:
            result[date] = []
        result[date].append("Essen %s: %s" % (n, food))
    # Saturdays and sundays do not occur on the site, so add [] manually
    result[get_next_weekday(5)] = []
    result[get_next_weekday(6)] = []
    return result


def format_date(date):
    return "%02d.%02d." % (date.day, date.month)


def get_next_weekday(day):
    today = datetime.today()
    diff = (day - today.weekday()) % 7
    return format_date(today + timedelta(days=diff))


def get_today_menus():
    date = format_date(datetime.today())
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


def override_current_menus():
    for m in get_all_mensa_subscriptions():
        data = retrieve_menus(m)
        for d in data:
            remove_menus(m, d)
        add_menus(m, data)


def edit_distance(s1, s2):
    if len(s1) < len(s2):
        return edit_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            current_row.append(min(previous_row[j+1] + 1, current_row[j] + 1,
                                   previous_row[j] + (c1 != c2)))
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
