from datetime import datetime
from playhouse.shortcuts import model_to_dict
import models


class UsersDAO:
    def __init__(self):
        self.users = models.Users

    def add_user(self, user_id, chat_id):
        self.users.create_or_get(user_id=user_id, chat_id=chat_id, signup_date=datetime.now())
