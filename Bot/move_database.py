from database import Database
import os
import sys
from datetime import datetime
import sqlite3
import re


def move_database(old_db, new_db):
    if os.path.exists(new_db):
        print(new_db, "already exists, skipping to avoid overwriting it.")
        return
    connection = sqlite3.connect(old_db)
    cursor = connection.cursor()
    cursor.execute("select * from menus")
    menus = cursor.fetchall()
    cursor.execute("select * from users")
    users = cursor.fetchall()
    connection.close()
    db = Database(new_db)
    for u, m in users:
        db.add_mensa_subscription(u, m)
    menus_by_mensa = {}
    for mensa, date, menu in menus:
        d = date.split(".")
        try:
            dt = datetime(int(d[2]) if d[2] else 2020, int(d[1]), int(d[0]))
        except ValueError:
            print("Invalid date", date)
            continue
        if menu:
            title, _, rest = menu.partition(": ")
            desc = re.sub(r'&#x\S+', "", rest).strip()
            ing = " ".join(re.findall(r'(&#x\S+)', rest))
            db.add_menus(mensa, {dt: [(title, desc, ing)]})
        else:
            db.add_menus(mensa, {dt: []})

if __name__ == "__main__":
    a = sys.argv
    if len(a) != 3:
        print(f"Usage: python3 {a[0]} old_db new_db")
        sys.exit(1)
    move_database(a[1], a[2])
