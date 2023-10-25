from urllib.request import urlopen
import json
from datetime import datetime


MENSA_IDS = {'Mensa Shedhalle': '611', 'Mensa Nürtingen': '665',
             'Mensa Reutlingen': '630', 'Mensa Morgenstelle': '621',
             'Mensa Hohenheim': '661', 'Mensa Sigmaringen': '640',
             'Mensa Albstadt-Ebingen': '645', 'Mensa Rottenburg': '655',
             'Cafeterien MM/HSZ/San/TTR': '724', 'Mensa Prinz Karl': '623'}


def is_supported(mensa):
    return mensa in MENSA_IDS


def retrieve_menus(mensa):
    id = MENSA_IDS[mensa]
    with urlopen("https://www.my-stuwe.de/wp-json/mealplans/v1/canteens/" +
                 id) as u:
        d = json.load(u)
    res = {}
    for m in d[id]["menus"]:
        date = format_date(m['menuDate'])
        if date not in res:
            res[date] = []
        # TODO: Extract emojis
        res[date].append((m['menuLine'], ', '.join(m['menu']), ""))
    return res


def format_date(date):
    y, m, d = date.split("-")
    return datetime(int(y), int(m), int(d))
