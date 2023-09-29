#!/usr/bin/env python3
"""Module to store hashed user strings in dbm and retrive secure user strings"""

import os
import dbm
import json
import uuid
import base64
from dotenv import load_dotenv
from argon2 import PasswordHasher

load_dotenv()

class UserDBManager:
    """Main DB Manager for IRs
    """
    def __init__(self):
        """Initialize the SecureUserStorage instance with a unique identifier."""
        self.secret_key = os.getenv("HMAC_SECRET_KEY").encode('utf-8')
        self.get_path = os.path.expanduser(os.getenv("GET_PATH"))
        self.unique_identifier = str(uuid.uuid4())
        self.file_name = f"user_db_{self.unique_identifier}"
        self.file_path = os.path.join(self.get_path, self.file_name)
        self.initialize_db()


    def initialize_db(self):
        """Initialize the user-specific database if it doesn't exist."""
        # Ensure the directory exists or create it
        os.makedirs(self.get_path, exist_ok=True)

        # Create an empty file named 'user_db' inside the directory
        with open(self.file_path, 'w', encoding="utf-8"):
            pass

        self._initialize_user_db()

    def _initialize_user_db(self):
        """Initialize the keys in the user-specific database."""
        with dbm.open(self.file_path, 'n') as individual_store:
            individual_store['_id'] = b''
            individual_store['hash_string'] = b''
            individual_store['secured_user_string'] = b''

    def serialize_data(self, data):
        """Serialize data to a JSON string."""
        if 'request_string' in data:
            return json.dumps(data['request_string'])
        else:
            raise KeyError("Error parsing key")


    def deserialize_data(self, data_str):
        """Deserialize a JSON string to the original data."""
        return json.loads(data_str)

    def hash_user_string(self, user_str):
        """Hash the user string using SHA-256."""
        user_str_bytes = user_str.encode('utf-8')
        p_hash = PasswordHasher()
        hashed_user_string = p_hash.hash(user_str_bytes)
        return hashed_user_string

    def store_user_string(self, request_data):
        """Store user string after encryption and generate
        secure user string using b64 encoding 
        """

        data = self.serialize_data(request_data)
        user_hash = self.hash_user_string(data)

        with dbm.open(self.file_path, 'w') as individual_store:
            individual_store['hash_string'] = user_hash.encode('utf-8)')

            hash_string = individual_store.get('hash_string')
            if hash_string:
                secure_user_string = base64.urlsafe_b64encode(hash_string).decode('utf-8')[12:24]
                individual_store['secured_user_string'] = secure_user_string
                individual_store['_id'] = self.unique_identifier.encode('utf-8')

    def display_user_db(self):
        """Display the contents of the user-specific database."""
        with dbm.open(self.file_path, 'r') as individual_store:
            for key in individual_store.keys():
                try:
                    key_str = key.decode('utf-8')
                except UnicodeDecodeError:
                    key_str = key.hex()

                try:
                    value_str = individual_store[key].decode('utf-8')
                except UnicodeDecodeError:
                    value_str = individual_store[key].hex()

                print(f"Key: {key_str}, Value: {value_str}")
