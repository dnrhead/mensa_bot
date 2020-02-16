from db_tools import get_all_user_and_mensas

users_mensas = get_all_user_and_mensas()
print("unique sending messages %d" % len(users_mensas))

print("unique users %d" % len(set([i[0] for i in users_mensas])))
print("unique mensas %d" % len(set([i[1] for i in users_mensas])))
print("list of mensas: ")
print(set([i[1] for i in users_mensas]))
