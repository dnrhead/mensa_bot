from utils import edit_distance
# Additional mensas need to be imported and added here
import mensa_swfr
import mensa_tuebingen
MENSA_MODULES = [mensa_swfr, mensa_tuebingen]


def retrieve_menus(mensa):
    module_candidates = [m for m in MENSA_MODULES if m.is_supported(mensa)]
    assert len(module_candidates) == 1
    return module_candidates[0].retrieve_menus(mensa)


def fetch_all_menus(config, date):
    db = config.get_database()
    result = {}
    # TODO: Only get menus for mensas in the config
    for m in db.get_all_mensa_subscriptions():
        menus = db.get_menus(m, date)
        if menus == []:
            try:
                data = retrieve_menus(m)
                db.add_menus(m, data)
                if date in data:
                    menus = data[date]
            except Exception as e:
                # An error occured during retrieving the menus, just use []
                print(f"Retrieving menus for {m} raised the exception '{e}'.")
                menus = []
        # Filter out menus where the title is none
        result[m] = list(filter(lambda x: x[0], menus))
    return result


def overwrite_current_menus(config):
    db = config.get_database()
    for m in db.get_all_mensa_subscriptions():
        try:
            data = retrieve_menus(m)
        except Exception as e:
            # An error occured during retrieving the menus, just continue
            print(f"Retrieving menus for {m} raised the exception '{e}'.")
            continue
        for d in data:
            db.remove_menus(m, d)
        db.add_menus(m, data)


def format_mensa_list(mensa_list, order):
    mensa_indices = sorted((order.index(m) + 1, m) for m in mensa_list
                           if m in order)
    return "\n".join("(%d)\t%s" % i for i in mensa_indices)


def get_matching_mensa(match, list):
    n = match.strip("() ")
    if n.isdigit():
        index = int(n) - 1
        if index < len(list):
            return list[index]
    min_ed = 3
    res = None
    for m in list:
        for m2 in get_variants(m):
            ed = edit_distance(m2, match.lower())
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
        variants.update(v.replace(*r).strip() for v in list(variants))
    return variants
