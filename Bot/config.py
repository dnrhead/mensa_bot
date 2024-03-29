import json
import os
from database import Database


class Config:
    def __init__(self, path):
        with open(path) as f:
            d = json.load(f)
        self.__admin_ids = d["admin_ids"]
        self.__token = d["token"]
        self.__mensas = d["mensas"]
        # Use the absolute path for the database based on the config
        config_dir = os.path.dirname(path)
        db_path = os.path.abspath(os.path.join(config_dir, d["database"]))
        self.__database = Database(db_path)

    def get_admin_ids(self):
        return self.__admin_ids

    def get_token(self):
        return self.__token

    def get_mensas(self):
        return self.__mensas

    def get_database(self):
        return self.__database
