"""Module to sync with individual stores (IRs)"""
import os
import redis
from dotenv import load_dotenv
from user_store import user_db_manager

load_dotenv()



class CentralStore(user_db_manager.UserDBManager):
    """Initialise main store for real-time syncing"""

    _r = redis.Redis(host=os.getenv("HOST"), port=os.getenv("REDIS_PORT"), decode_responses=True)



req = {"uid": "1bfc4b8d-ab42-4e73-b21f-1f19d676fd8e", "request_string":"tailordb12345tyrgehp"}

x = CentralStore()

print(x.locate_db_by_uid_and_verify(req))