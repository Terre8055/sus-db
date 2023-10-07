import os
from dotenv import load_dotenv
from redis_om import get_redis_connection


load_dotenv()
# REDIS CLOUD CONN

redis = get_redis_connection(
    host=os.getenv('HOST'),
    port=os.getenv('PORT'),
    password=os.getenv('PASSWORD'),
    decode_responses=True,
)