"""Module for user-defined configurations"""
import os

from dotenv import load_dotenv
from redis_om import get_redis_connection


load_dotenv()

# DBM CONFIGURATION
db_file_name = 'user_db'
get_path = os.getenv('GET_PATH')
get_log_path = os.getenv('LOG_PATH')


# REDIS CLOUD CONN

redis = get_redis_connection(
    host=os.getenv('REDIS_MASTER_HOST'),
    port=os.getenv('REDIS_PORT_NUMBER'),
    password=os.getenv('REDIS_PASSWORD'),
    decode_responses=True,
)