import sqlite3
from utils import format_date


class Database:
    def __init__(self, db_path):
        self.__db_path = db_path
        self.__execute_sql("CREATE TABLE IF NOT EXISTS users "
                           "(user VARCHAR(30), mensa VARCHAR(30));")
        self.__execute_sql("CREATE TABLE IF NOT EXISTS menus "
                           "(mensa VARCHAR(30), date VARCHAR(30), "
                           "title VARCHAR(50), description VARCHAR(200),"
                           "ingredients VARCHAR(50));")

    def __execute_sql(self, cmd):
        connection = sqlite3.connect(self.__db_path)
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
        return [i[0] for i in self.__execute_sql("SELECT DISTINCT user FROM "
                                                 "users")]

    def get_menus(self, mensa, date):
        return self.__execute_sql("SELECT DISTINCT title, description, "
                                  "ingredients FROM menus WHERE "
                                  "mensa=%r AND date=%r AND title IS NOT NULL"
                                  % (mensa, format_date(date)))

    def add_menus(self, mensa, data):
        values = []
        for date, menus in data.items():
            fd = format_date(date)
            if menus:
                values.extend("(%r, %r, %r, %r, %r)" % (mensa, fd, t, d, i)
                              for t, d, i in menus)
            else:
                values.append("(%r, %r, NULL, NULL, NULL)" % (mensa, fd))
        if values:
            self.__execute_sql("INSERT INTO menus VALUES %s;" %
                               ", ".join(values))

    def remove_menus(self, mensa, date):
        self.__execute_sql("DELETE FROM menus WHERE mensa=%r AND date=%r" %
                           (mensa, format_date(date)))
