import re
from db_tools import get_all_menus

EXCLUDE_WORDS = ["essen", "oder", "wahl", "schneller", "teller", "pavillon",
                 "spezialitäten", "außerdem", "buffet", "auswahl", "wunsch",
                 "bunter", "geriebener", "gebackenes"]
FOOD_TYPES = {"x1F331": "vegetarisch", "x1F414": "Geflügel", "x1F411": "Lamm",
              "x1F41F": "Fisch", "x1F416": "Schwein", "x1F404": "Rind"}


def get_food_counts(mensa):
    d = {}
    for m in get_all_menus(mensa):
        words = re.findall(r'(\w+)', m)
        for w in words:
            if w.islower() or len(w) < 4 or w.lower() in EXCLUDE_WORDS:
                continue
            d[w] = d.get(w, 0) + 1
    return sorted(d.items(), key=lambda x: -x[1])


def get_food_type_counts(mensa):
    return [(FOOD_TYPES[i], c) for i, c in get_food_counts(mensa)
            if i in FOOD_TYPES]
