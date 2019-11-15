from urllib.request import urlopen
import re

mensas = ['Mensa Rempartstrasse', 'Mensa Institutsviertel',
          'Mensa Littenweiler', 'Mensa Flugplatz', 'Mensa Furtwangen',
          'Mensa Offenburg', 'Mensa Gengenbach', 'Mensa Kehl',
          'Mensa Schwenningen', 'Mensa Trossingen',
          'Ausgabestelle EH Freiburg', 'MusiKantine', 'OHG Furtwangen']


def get_data(mensa):
    assert mensa in mensas
    mensa_transformed = mensa.lower().replace(" ", "-")
    with urlopen("https://www.swfr.de/essen-trinken/speiseplaene/"
                 + mensa_transformed) as url:
        txt = url.read().decode()
    result = {}
    for i in txt.split("<h3>"):
        split = i.split("</h3>")
        if len(split) != 2:
            continue
        day2, rest = split
        day = day2.split(" ")[1]
        menus = re.findall(r'<h4.*?>(.*?)</h4><div.*?>\s*(.*?)<span', rest)
        if menus:
            result[day] = [(t, f.replace("<br>", " ").strip())
                           for t, f in menus]
    return result

print(get_data(mensas[3]))