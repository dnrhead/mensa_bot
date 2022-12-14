from urllib.request import urlopen
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import db_tools

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


def format_swfr_menu(title, flag, desc, ingredients):
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
    suffix = f"freiburg/{mensa_url}" if mensa in mensas_freiburg else mensa_url
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


def retrieve_menus_swfr(mensa):
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
            menus.append(format_swfr_menu(title, get_flag(c), desc,
                                          get_ingredients(c)))
        day, month = date_match.groups()
        date = get_date_with_year(int(day), int(month))
        result[format_date(date)] = menus
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
    for m in db_tools.get_all_mensa_subscriptions():
        menus = db_tools.get_menus(m, date)
        if menus == []:
            try:
                data = retrieve_menus(m)
                db_tools.add_menus(m, data)
                if date in data:
                    menus = data[date]
            except:
                # An error occured during retrieving the menus, just use []
                menus = []
        result[m] = list(filter(bool, menus))
    return result


def overwrite_current_menus():
    for m in db_tools.get_all_mensa_subscriptions():
        try:
            data = retrieve_menus(m)
        except:
            continue
        for d in data:
            db_tools.remove_menus(m, d)
        db_tools.add_menus(m, data)


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
