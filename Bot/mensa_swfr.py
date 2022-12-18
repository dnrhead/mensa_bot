from urllib.request import urlopen
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

MENSAS_FREIBURG = ['Mensa Rempartstrasse', 'Mensa Institutsviertel',
                   'Mensa Littenweiler', 'Mensa Flugplatz',
                   'Ausgabestelle EH Freiburg', 'MusiKantine']
SUPPORTED_MENSAS = MENSAS_FREIBURG + ['Mensa Furtwangen', 'OHG Furtwangen',
                                      'Mensa Offenburg', 'Mensa Gengenbach',
                                      'Mensa Kehl', 'Mensa Schwenningen',
                                      'Mensa Trossingen', 'Mensa Loerrach']
MONTHS = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
          "August", "September", "Oktober", "November", "Dezember"]


def retrieve_menus(mensa):
    with urlopen(get_swfr_url(mensa)) as url:
        bs = BeautifulSoup(url, "lxml")
    result = {}
    for d in bs.findAll("div", {"class": "menu-tagesplan"}):
        h3 = d.findChild("h3")
        if not h3:
            continue
        date_match = re.search(r'(\d+)\.(\d+)\.', h3.getText())
        if not date_match:
            continue
        menus = []
        for c in d.findChildren("div", {"class": "col-span-1 bg-lighter-cyan py-20px px-15px flex flex-col"}):
            title = c.find("h5").getText()
            desc = c.find("small", {"class": "extra-text mb-15px"}).getText(", ").replace(":,", ":")
            menus.append(format_menu(title, get_flag(c), desc,
                                     get_ingredients(c)))
        day, month = date_match.groups()
        date = get_date_with_year(int(day), int(month))
        result[date] = menus
    # Sundays do not occur on the site, therefore add [] manually
    result[get_next_weekday(6)] = []
    return result


def format_menu(title, flag, desc, ingredients):
    def matches(*args):
        return any(x in desc.lower() for x in args)
    res = title
    if flag in ["vegan", "vegetarisch"]:
        res += f" ({flag}): {desc} &#x1F331"
    elif flag == "vegan-aufwunsch":
        res += f" (auf Wunsch vegan): {desc} &#x1F331"
    else:
        res += f": {desc}"
        if matches(" veg"):
            res += " &#x1F331"
    if matches("hähn", "huhn", "hühn", "pute", "flügel"):
        res += " &#x1F414"
    if matches("lamm"):
        res += " &#x1F411"
    if "sch" in ingredients:
        res += " &#x1F416"
    if "ri" in ingredients:
        res += " &#x1F404"
    if "nF" in ingredients or \
       matches("fisch", "pangasius", "lachs", "forelle", "meeres"):
        res += " &#x1F41F"
    return res


def get_swfr_url(mensa):
    mensa_url = mensa.lower().replace(" ", "-")
    suffix = f"freiburg/{mensa_url}" if mensa in MENSAS_FREIBURG else mensa_url
    return "https://www.swfr.de/essen/mensen-cafes-speiseplaene/" + suffix


def get_flag(bs_element):
    match = bs_element.find("img", {"class": "w-30px"})
    if match:
        return re.search(r'/([^/]*?)\.svg',
                         match.get_attribute_list("src")[0]).group(1)


def get_ingredients(bs_element):
    match = bs_element.find("small", {"x-show": "!showAllergenes"})
    if not match:
        return []
    return match.contents[2].split(",")


def get_date_with_year(day, month):
    today = datetime.today()
    year = today.year
    if today.month > month:
        year += 1
    return datetime(year, month, day)


def get_next_weekday(day):
    today = datetime.today()
    diff = (day - today.weekday()) % 7
    return today + timedelta(days=diff)
