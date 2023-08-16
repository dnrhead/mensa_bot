def format_date(date):
    return "%02d.%02d.%d" % (date.day, date.month, date.year)


def format_menus(mensa, menus, date):
    res = f"<u><b>{mensa} ({format_date(date)})</b></u>"
    for t, d, i in menus:
        res += f"\n\n<b>{t} {i}</b>\n{d}"
    return res


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
