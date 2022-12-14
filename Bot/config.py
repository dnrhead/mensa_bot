import json

class Config:
    def __init__(self, config_name):
        with open(config_name) as f:
            d = json.load(f)
        self.__admin_ids = d["admin_ids"]
        self.__token = d["token"]
    
    def get_admin_ids(self):
        return self.__admin_ids

    def get_token(self):
        return self.__token
