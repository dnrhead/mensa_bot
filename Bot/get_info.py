from database import Database

# TODO: We should not hardcode the filename here
db = Database("database.db")

users_mensas = db.get_all_user_and_mensas()
print("unique sending messages %d" % len(users_mensas))
print("unique users %d" % len(db.get_users()))

mensas = db.get_all_mensa_subscriptions()
print("unique mensas %d" % len(mensas))
print("list of mensas: ")
print(mensas)
