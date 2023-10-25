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
    with urlopen("https://www.my-stuwe.de/wp-json/mealplans/v1/canteens/" +
                 MENSA_IDS[mensa]) as u:
        d = json.load(u)
    res = {}
    for i in d.values():
        menus = {}
        for m in i["menus"]:
            date = format_date(m['menuDate'])
            if date not in menus:
                menus[date] = []
            # TODO: Extract emojis
            menus[date].append((m['menuLine'], ', '.join(m['menu']), ""))
        return menus


def format_date(date):
    y, m, d = date.split("-")
    return datetime(int(y), int(m), int(d))
