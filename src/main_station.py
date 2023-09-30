"""Module to sync with individual stores (IRs)"""
import os
import redis
from dotenv import load_dotenv
from user_store import user_db_manager

load_dotenv()


r = redis.Redis(host=os.getenv("HOST"), port=os.getenv("REDIS_PORT"), decode_responses=True)

class CentralStore(user_db_manager.UserDBManager):
    """Initialise main store for real-time syncing"""
