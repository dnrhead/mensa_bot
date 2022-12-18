import json
from database import Database


class Config:
    def __init__(self, config_name):
        with open(config_name) as f:
            d = json.load(f)
        self.__admin_ids = d["admin_ids"]
        self.__token = d["token"]
        self.__mensas = d["mensas"]
        self.__database = Database(d["db_name"])

    def get_admin_ids(self):
        return self.__admin_ids

    def get_token(self):
        return self.__token

    def get_mensas(self):
        return self.__mensas

    def get_database(self):
        return self.__database
