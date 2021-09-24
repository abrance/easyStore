import json

from flask_login import UserMixin
from app.config import Config


class User(UserMixin):
    def __init__(self, id_number):
        self.users = {}
        self.init_db()
        self.user_id = self.users.get(id_number)

    def init_db(self):
        db = open(Config.root_path / 'db', '+')
        data = json.load(db)

        if data:
            pass
        else:
            data = {
                # user_id 为key, value为键值对
                "users": {}
            }
            # 每次做出的修改都需要dump一次
            json.dump(Config.root_path / 'db', data)
        self.users = data.get("users")
