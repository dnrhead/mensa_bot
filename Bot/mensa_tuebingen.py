from urllib.request import urlopen
import json


def retrieve_menus():
    with urlopen("https://www.my-stuwe.de/wp-json/mealplans/v1/canteens/") \
         as u:
        d = json.load(u)
    res = {}
    for i in d.values():
        menus = {}
        for m in i["menus"]:
            date = format_date(m['menuDate'])
            if date not in menus:
                menus[date] = []
            menus[date].append(f"{m['menuLine']}: {', '.join(m['menu'])}")
        res[i["canteen"]] = menus
    return res


def format_date(date):
    return ".".join(reversed(date.split("-")))
