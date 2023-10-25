"""Module for user-defined configurations"""
import os

from dotenv import load_dotenv
from redis_om import get_redis_connection


load_dotenv()

# DBM CONFIGURATION
db_file_name = os.getenv('FILE_NAME')
get_path = os.getenv('GET_PATH')
get_log_path = os.getenv('LOG_PATH')


# REDIS CLOUD CONN

redis = get_redis_connection(
    host=os.getenv('HOST'),
    port=os.getenv('PORT'),
    password=os.getenv('PASSWORD'),
    decode_responses=True,
)