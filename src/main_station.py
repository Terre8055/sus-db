"""Module to sync with individual stores (IRs)"""
import os
import redis
from dotenv import load_dotenv
from user_store import user_db_manager

load_dotenv()



class CentralStore(user_db_manager.UserDBManager):
    """Initialise main store for real-time syncing"""


    def connect(self):
        print('Connection initalised.........')
        connection = redis.Redis(
            host=os.getenv('HOST'),
            port=os.getenv('PORT'),
            password=os.getenv('PASSWORD')
            )
        if connection:
            return 'Connection successfully established!'




x = CentralStore()
print(x.connect())