"""Module for user-defined configurations"""
import os

from dotenv import load_dotenv

load_dotenv()

# DBM CONFIGURATION
db_file_name = os.getenv('FILE_NAME')
get_path = os.getenv('GET_PATH')
