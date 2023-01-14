import sqlite3
import os
from utils import format_date


class Database:
    def __init__(self, db_name):
        self.__db_name = db_name
        self.__execute_sql("CREATE TABLE IF NOT EXISTS users "
                           "(user VARCHAR(30), mensa VARCHAR(30));")
        self.__execute_sql("CREATE TABLE IF NOT EXISTS menus "
                           "(mensa VARCHAR(30), date VARCHAR(30), "
                           "menu VARCHAR(200));")

    def __execute_sql(self, cmd):
        dirname = os.path.dirname(os.path.abspath(__file__))
        dbpath = os.path.join(dirname, self.__db_name)
        connection = sqlite3.connect(dbpath)
        cursor = connection.cursor()
        cursor.execute(cmd)
        result = cursor.fetchall()
        connection.commit()
        connection.close()
        return result

    def add_mensa_subscription(self, user, mensa):
        self.__execute_sql("INSERT INTO users VALUES (%r, %r);"
                           % (user, mensa))

    def remove_mensa_subscription(self, user, mensa):
        self.__execute_sql("DELETE FROM users WHERE user=%r AND mensa=%r" %
                           (user, mensa))

    def remove_mensa_subscriptions(self, user):
        self.__execute_sql("DELETE FROM users WHERE user=%r" % user)

    def get_mensas_subscription(self, user):
        return [i[0] for i in self.__execute_sql("SELECT DISTINCT mensa FROM "
                                                 "users WHERE user=%r" % user)]

    def get_all_mensa_subscriptions(self):
        return [i[0] for i in self.__execute_sql("SELECT DISTINCT mensa FROM "
                                                 "users")]

    def get_all_user_and_mensas(self):
        return self.__execute_sql("SELECT DISTINCT * FROM users")

    def get_users(self):
        return [i[0] for i in self.__execute_sql("SELECT DISTINCT user FROM"
                                                 "users")]

    def get_menus(self, mensa, date):
        return [i[0] for i in
                self.__execute_sql("SELECT DISTINCT menu FROM menus WHERE "
                                   "mensa=%r AND date=%r"
                                   % (mensa, format_date(date)))]

    def get_all_menus(self, mensa):
        return [i[0] for i in
                self.__execute_sql("SELECT menu FROM menus WHERE mensa=%r "
                                   "AND menu IS NOT NULL" % mensa)]

    def add_menus(self, mensa, data):
        if not data:
            return
        values = []
        for d in data:
            fd = format_date(d)
            if data[d]:
                values.extend("(%r, %r, %r)" % (mensa, fd, f) for f in data[d])
            else:
                values.append("(%r, %r, NULL)" % (mensa, fd))
        self.__execute_sql("INSERT INTO menus VALUES %s;" % ", ".join(values))

    def remove_menus(self, mensa, date):
        self.__execute_sql("DELETE FROM menus WHERE mensa=%r AND date=%r" %
                           (mensa, format_date(date)))
