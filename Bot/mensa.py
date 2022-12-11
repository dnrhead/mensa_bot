from urllib.request import urlopen
import re
from datetime import datetime, timedelta
from db_tools import *

mensas_freiburg = ['Mensa Rempartstrasse', 'Mensa Institutsviertel',
                   'Mensa Littenweiler', 'Mensa Flugplatz',
                   'Ausgabestelle EH Freiburg', 'MusiKantine']
swfr_mensas = mensas_freiburg + ['Mensa Furtwangen', 'OHG Furtwangen',
                                 'Mensa Offenburg', 'Mensa Gengenbach',
                                 'Mensa Kehl', 'Mensa Schwenningen',
                                 'Mensa Trossingen', 'Mensa Loerrach']
mensas = swfr_mensas + ['Fraunhofer IPM Kantine']

MONTHS = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
          "August", "September", "Oktober", "November", "Dezember"]

def retrieve_menus(mensa):
    if mensa in swfr_mensas:
        return retrieve_menus_swfr(mensa)
    if mensa == 'Fraunhofer IPM Kantine':
        return retrieve_menus_ipm()
    raise NotImplementedError("Unhandled case: %r" % mensa)


def format_swfr_menu(menu):
    title, flag, desc, ingredients = menu

    def matches(*args):
        return any(x in desc.lower() for x in args)
    formatted_desc = desc.replace("<br>", ", ")
    res = title
    m = re.search(r'/([^/]*?)\.svg', flag)
    if not m:
        res += f": {formatted_desc}"
        if matches(" veg"):
            res += " &#x1F331"
    else:
        v = m.group(1)
        if v in ["vegan", "vegetarisch"]:
            res += f" ({v}): {formatted_desc} &#x1F331"
        elif v == "vegan-aufwunsch":
            res += f" (auf Wunsch vegan): {formatted_desc} &#x1F331"
    if matches("hähn", "huhn", "hühn", "pute", "flügel"):
        res += " &#x1F414"
    if matches("lamm"):
        res += " &#x1F411"
    i = ingredients.split(",")
    if "sch" in i:
       res += " &#x1F416"
    if "ri" in i:
        res += " &#x1F404"
    if "nF" in i or matches("fisch", "pangasius", "lachs", "forelle", "meeres"):
        res += " &#x1F41F"
    return res


def get_swfr_url(mensa):
    mensa_url = mensa.lower().replace(" ", "-")
    suffix = f"freiburg/{mensa_url}" if mensa in mensas_freiburg else mensa_url
    return "https://www.swfr.de/essen/mensen-cafes-speiseplaene/" + suffix


def retrieve_menus_swfr(mensa):
    with urlopen(get_swfr_url(mensa)) as url:
        txt = url.read().decode()
    result = {}
    for i in txt.split("<h3>"):
        m = re.search(r'(\d+)\.(\d+)\..*?</h3>(.*)', i, re.DOTALL)
        if not m:
            continue
        day, month, table = m.groups()
        menus = re.findall(r'<h5>(.*?)</h5>\s*(.*?)\s*</div>\s*<small.*?>(.*?)'
                           r'</small>.*?(?:<small class="zusatzsstoffe" x-show'
                           r'="!showAllergenes">Kennzeichnungen/Zusatzstoffe:'
                           r'\s*(.*?)<br>)?', table, re.DOTALL)
        date = get_date_with_year(int(day), int(month))
        result[format_date(date)] = list(map(format_swfr_menu, menus))
    # Sundays do not occur on the site, therefore add [] manually
    result[get_next_weekday(6)] = []
    return result


def retrieve_menus_ipm():
    with urlopen("https://www.ipm.fraunhofer.de/de/ueber-fraunhofer-ipm/"
                 "fraunhofer-ipm-kantine.html") as url:
        txt = url.read().decode()
    result = {}
    for b in re.findall(r'<tbody>(.*?)</tbody>', txt, re.DOTALL):
        m = re.search(r'<h4>(.*?),\s*(\d+)\.', b)
        if not m:
            continue
        start_date = get_date_with_year(int(m.group(2)),
                                        MONTHS.index(m.group(1)) + 1)
        menus = re.findall(r'<tr>\s*<td>.*?</td>\s*<td>(.*?)</td>', txt,
                           re.DOTALL)
        for i in range(7):
            raw = menus[i] if i < len(menus) else ""
            day = format_date(start_date + timedelta(i))
            result[day] = []
            raw_meals = re.findall(r'<li>(.*?)</li>', raw)
            for j, r in enumerate(raw_meals, 1):
                tp = re.search("<i>(.*?)</i>", r)
                meal = re.sub(r'\s*<sup>.*?</sup>', "", r.replace(
                    tp.group(0), "").replace("&nbsp;", "")).strip() + " " + \
                    " ".join(get_icons(tp.group(1)))
                result[day].append(f"Essen {j:}: {meal:}")
    return result


def get_icons(txt):
    txt2 = txt.lower()
    res = []
    if "schwein" in txt2:
        res.append("&#x1F416")
    if "rind" in txt2:
        res.append("&#x1F404")
    if "veg" in txt2:
        res.append("&#x1F331")
    if "fisch" in txt2:
        res.append("&#x1F41F")
    return res


def get_date_with_year(day, month):
    today = datetime.today()
    year = today.year
    if today.month > month:
        year += 1
    return datetime(year, month, day)
    

def format_date(date):
    return "%02d.%02d.%d" % (date.day, date.month, date.year)


def get_next_weekday(day):
    today = datetime.today()
    diff = (day - today.weekday()) % 7
    return format_date(today + timedelta(days=diff))


def fetch_all_menus(date):
    result = {}
    for m in get_all_mensa_subscriptions():
        menus = get_menus(m, date)
        if menus == []:
            try:
                data = retrieve_menus(m)
                add_menus(m, data)
                if date in data:
                    menus = data[date]
            except:
                # An error occured during retrieving the menus, just use []
                menus = []
        result[m] = list(filter(bool, menus))
    return result


def override_current_menus():
    for m in get_all_mensa_subscriptions():
        try:
            data = retrieve_menus(m)
        except:
            continue
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


def format_mensa_list(mensa_list=None):
    if mensa_list is None:
        mensa_indices = enumerate(mensas, 1)
    else:
        mensa_indices = sorted((mensas.index(m) + 1, m) for m in mensa_list)
    return "\n".join("(%d)\t%s" % i for i in mensa_indices)


def get_matching_mensa(mensa):
    n = mensa.strip("() ")
    if n.isdigit():
        index = int(n) - 1
        if index < len(mensas):
            return mensas[index]
    min_ed = 3
    res = None
    for m in mensas:
        for m2 in get_variants(m):
            ed = edit_distance(m2, mensa.lower())
            if ed == 0:
                return m
            if ed < min_ed:
                min_ed = ed
                res = m
    return res


def get_variants(mensa):
    replacements = {"mensa": "", "ae": "ä", "oe": "ö", "ue": "ü", "ss": "ß"}
    variants = {mensa.lower()}
    for r in replacements.items():
        newVariants = set()
        for v in variants:
            newVariants.add(v.replace(*r).strip())
        variants |= newVariants
    return variants
