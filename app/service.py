from django.core.cache import cache

def add_remove_online_user(action, username):
    online_users = cache.get('online_users')
    if not online_users:
        online_users = set()
    if action == "add":
        online_users.add(username)
    elif action == "remove":
        online_users.discard(username)
    else:
        return False
    print(action, username)
    cache.set("online_users" ,online_users)
    return online_users