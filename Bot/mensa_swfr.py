from urllib.request import urlopen
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import ssl

MENSAS_FREIBURG = ['Mensa Rempartstrasse', 'Mensa Institutsviertel',
                   'Mensa Littenweiler', 'Mensa Flugplatz',
                   'Ausgabestelle EH Freiburg', 'MusiKantine']
SUPPORTED_MENSAS = MENSAS_FREIBURG + ['Mensa Furtwangen', 'OHG Furtwangen',
                                      'Mensa Offenburg', 'Mensa Gengenbach',
                                      'Mensa Kehl', 'Mensa Schwenningen',
                                      'Mensa Trossingen', 'Mensa Loerrach']
MONTHS = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
          "August", "September", "Oktober", "November", "Dezember"]


def is_supported(mensa):
    return mensa in SUPPORTED_MENSAS


def retrieve_menus(mensa):
    # TODO: Workaround
    with urlopen(get_swfr_url(mensa), context=ssl._create_unverified_context()) as url:
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
        attr = {"class":
                "col-span-1 bg-lighter-cyan py-20px px-15px flex flex-col"}
        for c in d.findChildren("div", attr):
            title, flag_match = c.find("h5")
            flag = flag_match.getText().strip()
            desc_match = c.find("small", {"class": "extra-text mb-15px"})
            desc = desc_match.getText(", ").replace(":,", ":")
            menus.append((format_title(title.strip(), flag), desc,
                          " ".join(get_ingredients(c, desc, flag))))
        day, month = date_match.groups()
        date = get_date_with_year(int(day), int(month))
        result[date] = menus
    # Sundays do not occur on the site, therefore add [] manually
    result[get_next_sunday(min(result))] = []
    return result



def format_title(title, flag):
    if flag in ["vegan", "vegetarisch"]:
        return f"{title} ({flag})"
    if flag == "vegan-aufwunsch":
        return f"{title} (auf Wunsch vegan)"
    return title


def get_swfr_url(mensa):
    mensa_url = mensa.lower().replace(" ", "-")
    suffix = f"freiburg/{mensa_url}" if mensa in MENSAS_FREIBURG else mensa_url
    return "https://www.swfr.de/essen/mensen-cafes-speiseplaene/" + suffix


def get_ingredients(bs_element, desc, flag):
    res = []
    def matches(*args):
        return any(x in desc.lower() for x in args)
    if flag.startswith("veg") or matches(" veg"):
        res.append("&#x1F331")
    if matches("hähn", "huhn", "hühn", "pute", "flügel"):
        res.append("&#x1F414")
    if matches("lamm"):
        res.append("&#x1F411")
    is_fish = matches("fisch", "pangasius", "lachs", "forelle", "meeres")
    if is_fish:
        res.append("&#x1F41F")
    match = bs_element.find("small", {"x-show": "!showAllergenes"})
    if not match:
        return res
    ing = match.contents[2].split(",")
    if "sch" in ing:
        res.append("&#x1F416")
    if "ri" in ing:
        res.append("&#x1F404")
    if "nF" in ing and not is_fish:
        res.append("&#x1F41F")
    return res


def get_date_with_year(day, month):
    today = datetime.today()
    year = today.year
    if today.month > month:
        year += 1
    return datetime(year, month, day)


def get_next_sunday(day):
    return day + timedelta(days=6-day.weekday())
