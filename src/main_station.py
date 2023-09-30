import os
import redis
from user_store import user_db_manager
from dotenv import load_dotenv

load_dotenv()


r = redis.Redis(host=os.getenv("HOST"), port=os.getenv("REDIS_PORT"), decode_responses=True)

print(r)
