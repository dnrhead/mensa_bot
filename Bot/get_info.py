from db_tools import get_all_user_and_mensas, get_all_mensa_subscriptions

users_mensas = get_all_user_and_mensas()
print("unique sending messages %d" % len(users_mensas))
print("unique users %d" % len(set(i[0] for i in users_mensas)))

mensas = get_all_mensa_subscriptions()
print("unique mensas %d" % len(mensas))
print("list of mensas: ")
print(mensas)
