"""Module for user-defined configurations"""
import os
from dotenv import load_dotenv
from redis_om import get_redis_connection


load_dotenv()

# DBM CONFIGURATION
db_file_name = os.getenv('FILE_NAME')
get_path = os.getenv('GET_PATH')
