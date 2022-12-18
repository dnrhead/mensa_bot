# TODO: We want to import also other modules (automatically?)
import mensa_swfr


def retrieve_menus(mensa):
    # TODO: We want to use other modules
    modules = [mensa_swfr]
    module_candidates = [m for m in modules if mensa in m.SUPPORTED_MENSAS]
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
        result[m] = list(filter(bool, menus))
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
    # TODO: We want to use the mensas from the config instead
    mensas = mensa_swfr.SUPPORTED_MENSAS
    if mensa_list is None:
        mensa_indices = enumerate(mensas, 1)
    else:
        mensa_indices = sorted((mensas.index(m) + 1, m) for m in mensa_list)
    return "\n".join("(%d)\t%s" % i for i in mensa_indices)


def get_matching_mensa(mensa):
    # TODO: We want to use the mensas from the config instead
    mensas = mensa_swfr.SUPPORTED_MENSAS
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
