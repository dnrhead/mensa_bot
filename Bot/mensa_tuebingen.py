from urllib.request import urlopen
import json
from datetime import datetime
import re


MENSA_IDS = {'Mensa Shedhalle': '611', 'Mensa Nürtingen': '665',
             'Mensa Reutlingen': '630', 'Mensa Morgenstelle': '621',
             'Mensa Hohenheim': '661', 'Mensa Sigmaringen': '640',
             'Mensa Albstadt-Ebingen': '645', 'Mensa Rottenburg': '655',
             'Cafeterien MM/HSZ/San/TTR': '724', 'Mensa Prinz Karl': '623'}

EMOJIS = {"F": "&#x1F41F", "G": "&#x1F414", "L": "&#x1F411", "R": "&#x1F404",
          "K": "&#x1F404", "S": "&#x1F416", "V": "&#x1F331",
          "vegan": "&#x1F331"}

REGEX = re.compile(r'\s*\[(.{1,10})\]')


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
        desc = ', '.join(m['menu'])
        ing = {EMOJIS[i] for x in REGEX.findall(desc)
               for i in x.split("/") if i in EMOJIS}
        title = m['menuLine']
        if "vegan" in desc:
            title += " (vegan)"
        res[date].append((title, REGEX.sub("", desc), " ".join(ing)))
    return res


def format_date(date):
    y, m, d = date.split("-")
    return datetime(int(y), int(m), int(d))
