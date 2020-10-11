from dataset import connect
from random import choice
from string import printable
from hashlib import sha512
from datetime import datetime
from os import makedirs
from os.path import isdir, abspath, dirname

KEY_USERS = "users"
KEY_MODULES = "modules"

DATETIME_FORMAT = "%d.%m.%Y %H:%M:%S"
DATE_FORMAT = "%d.%m.%Y"


class Database(object):
    db = None

    def __init__(self, database="carpi.db"):
        db_dir = abspath(dirname(database))
        if not isdir(db_dir):
            makedirs(db_dir, exist_ok=True)
        self.db = connect("sqlite:///" + abspath(database))

    @staticmethod
    def get_timestamp():
        return datetime.now().strftime(DATETIME_FORMAT)

    @staticmethod
    def get_date():
        return datetime.now().strftime(DATE_FORMAT)

    @staticmethod
    def parse_timestamp(timestamp):
        return datetime.strptime(timestamp, DATETIME_FORMAT)

    @staticmethod
    def parse_date(date):
        return datetime.strptime(date, DATE_FORMAT)

    @staticmethod
    def random_bytes(length=512, charset=printable) -> bytes:
        return bytes(''.join(choice(charset) for _ in range(length)), "utf-8")

    def get(self, tbl, key, value):
        return self.db[tbl].find_one(**{key: value})

    def get_user(self, username):
        return self.get(KEY_USERS, "username", username)

    def get_module(self, module):
        return self.get(KEY_MODULES, "name", module)

    def update_user(self, data):
        self.db[KEY_USERS].update(data, ["username"])

    def update_module(self, data):
        data["lastUpdated"] = self.get_timestamp()
        self.db[KEY_MODULES].update(data, ["name"])

    def update_last_username_lookup(self, username):
        u = self.get_user(username)
        if u:
            u["lastUsernameLookup"] = self.get_timestamp()
            self.update_user(u)
            return True
        return False

    def check_username_password(self, username: str, password: str) -> bool:
        u = self.get_user(username)
        if u:
            return u["password"] == password
        return False

    def check_username_cookie(self, username: str, cookie: str) -> bool:
        u = self.get_user(username)
        if u:
            return u["cookie"] == cookie
        return False

    def create_user(self, username: str) -> bool:
        u = self.get_user(username)
        if u:
            return False

        password = self.random_bytes(64)
        api_key = sha512(self.random_bytes())

        self.db[KEY_USERS].insert({
            "username": username,
            "password": password,
            "apiKey": api_key,
            "created": self.get_timestamp(),
            "lastLogin": self.get_timestamp(),
            "lastUsernameLookup": self.get_timestamp()
        })

    def delete_user(self, username: str) -> bool:
        u = self.get_user(username)
        if not u:
            return False
        self.db[KEY_USERS].delete(username=username)
        return True

    def create_module(self, name: str, source: str, description: str) -> bool:
        m = self.db[KEY_MODULES].find_one(name=name)
        if m is not None:
            return False
        self.db[KEY_MODULES].insert({
            "name": name,
            "source": source,
            "description": description,
            "created": self.get_date(),
            "lastUpdated": self.get_timestamp(),
            "downloads": 0
        })

    def delete_module(self, name) -> bool:
        m = self.db[KEY_MODULES].find_one(name=name)
        if m is None:
            return False
        self.db[KEY_MODULES].delete(name=name)

    @staticmethod
    def accumulate(tbl):
        r = []
        for i in tbl.all():
            r.append(i)
        return r

    @staticmethod
    def make_list(it):
        r = []
        for i in it:
            r.append(i)
        return r

    def get_modules(self):
        return self.accumulate(self.db[KEY_MODULES])

    def get_users(self):
        return self.accumulate(self.db[KEY_USERS])

    def get_oldest_module(self):
        r = self.make_list(self.db[KEY_MODULES].find(order_by=["created"]))
        if len(r) > 0:
            return r[0]
        return None

    def get_newest_module(self):
        r = self.make_list(self.db[KEY_MODULES].find(order_by=["created"]))
        if len(r) > 0:
            return r[-1]
        return None

    def get_module_count(self, created):
        return len(self.db[KEY_MODULES].find(created=created))

    @classmethod
    def get_timespan_date_days(cls, before: datetime, now=datetime.now()):
        return (now - before).days

    @classmethod
    def get_timespan_date_months(cls, before, now=datetime.now()):
        return (now - before).days / 30

    def get_created_timeline(self, timespan_calc, category="day"):
        r = []
        oldest = self.parse_date(self.get_oldest_module()["created"])
        newest = self.parse_date(self.get_newest_module()["created"])
        timespan = timespan_calc(oldest, newest)

        x = 0
        for _ in range(timespan):
            if category == "day":
                v = oldest.day + x
            elif category == "month":
                v = oldest.month + x
            else:
                return r

            r.append({
                category: v,
                "count": self.get_module_count(oldest)
            })

            x += 1
        return r

    def get_created_timeline_days(self):
        return self.get_created_timeline(self.get_timespan_date_days, "day")

    def get_created_timeline_months(self):
        return self.get_created_timeline(self.get_timespan_date_months, "month")

    def increment_module_download_count(self, name):
        m = self.get_module(name)
        if m:
            m["downloads"] += 1
            self.update_module(m)
            return True
        return False
