import re

EXCLUDE_WORDS = {"essen", "oder", "wahl", "schneller", "teller", "pavillon",
                 "spezialitäten", "außerdem", "buffet", "auswahl", "wunsch",
                 "bunter", "geriebener", "gebackenes", "regio", "dicke",
                 "woche", "paniertes", "mensa", "abendessen", "ausgabe",
                 "rempartstrasse", "rempartstraße", "wochenangebot",
                 "ausgabezeit", "buntes", "rote", "gebratener", "gebackener",
                 "gebackene", "newcomer"}
FOOD_TYPES = {"x1F331": "vegetarisch", "x1F414": "Geflügel", "x1F411": "Lamm",
              "x1F41F": "Fisch", "x1F416": "Schwein", "x1F404": "Rind"}


def get_food_counts(database, mensa):
    d = {}
    for m in database.get_all_menus(mensa):
        words = re.findall(r'(\w+)', m)
        for w in words:
            if w.islower() or len(w) < 4 or w.lower() in EXCLUDE_WORDS:
                continue
            d[w] = d.get(w, 0) + 1
    return sorted(d.items(), key=lambda x: -x[1])


def get_food_type_counts(database, mensa):
    return [(FOOD_TYPES[i], c) for i, c in get_food_counts(database, mensa)
            if i in FOOD_TYPES]
