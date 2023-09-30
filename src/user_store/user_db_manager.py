"""Module to store hashed user strings in dbm and retrive secure user strings"""

import os
import dbm
import json
import uuid
import datetime
import base64
import argon2
from dotenv import load_dotenv
from argon2 import PasswordHasher

load_dotenv()

class UserDBManager:
    """
    Main DB Manager for IRs.

    This class manages user-specific databases, allowing for the storage and retrieval
    of hashed and secured user strings.

    Attributes:
        secret_key (bytes): Secret key used for encryption and integrity verification.
        get_path (str): Path to the directory where user-specific databases are stored.
        unique_identifier (str): Unique identifier for this instance.
        file_name (str): Name of the database file, including the unique identifier.
        file_path (str): Full path to the database file.

    Methods:
        __init__(): Initialize the Storage instance with a unique identifier.
        initialize_db(): Initialize the user-specific database if it doesn't exist.
        _initialize_user_db(): Initialize the keys in the user-specific database.
        serialize_data(data): Serialize data to a JSON string.
        deserialize_data(data_str): Deserialize a JSON string to the original data.
        hash_user_string(user_str): Hash the user string using argon2.
        store_user_string(request_data): Store user string after encryption and generate
                                        secure user string using b64 encoding.
        verify_credential(user_string): Check validity of user string against hash.
        display_user_db(): Display the contents of the user-specific database.
        get_file_path: Retrieve store path on file.
        get_file_name: Retrieve store name on file.
        get_uuid: Retrieve store id on file.
        verify_user: locate db file on disk and verify user using uid
    """

    def __init__(self):
        """Initialize the SecureUserStorage instance with a unique identifier."""
        self.__get_path = os.path.expanduser(os.getenv("GET_PATH"))
        self.__unique_identifier = str(uuid.uuid4())
        self.__file_name = f"user_db_{self.__unique_identifier}"
        self.__file_path = os.path.join(self.__get_path, self.__file_name)
        self.initialize_db()


    def initialize_db(self):
        """Initialize the user-specific database if it doesn't exist."""
        # Ensure the directory exists or create it
        os.makedirs(self.__get_path, exist_ok=True)

        # Create an empty file named 'user_db' inside the directory
        with open(self.__file_path, 'w', encoding="utf-8"):
            pass

        self.__initialize_user_db()

    def __initialize_user_db(self):
        """Initialize the keys in the user-specific database."""
        with dbm.open(self.__file_path, 'n') as individual_store:
            individual_store['_id'] = b''
            individual_store['hash_string'] = b''
            individual_store['secured_user_string'] = b''
            individual_store['created_on'] = b''

    def serialize_data(self, data):
        """Serialize data to a JSON string."""
        if 'request_string' in data:
            return json.dumps(data['request_string'])
        raise KeyError("Error parsing key")


    def deserialize_data(self, data_str):
        """Deserialize a JSON string to the original data."""
        return json.loads(data_str)

    def hash_user_string(self, user_str):
        """Hash the user string using argon2"""
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

        with dbm.open(self.__file_path, 'w') as individual_store:
            individual_store['hash_string'] = user_hash.encode('utf-8)')

            hash_string = individual_store.get('hash_string')

            current_datetime = datetime.datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%dT%H:%M:%S.%f")

            cur_date = datetime.datetime.strptime(formatted_datetime, "%Y-%m-%dT%H:%M:%S.%f")

            if hash_string is not None:
                secure_user_string = base64.urlsafe_b64encode(hash_string).decode('utf-8')[12:24]
                individual_store['secured_user_string'] = secure_user_string
                individual_store['_id'] = self.__unique_identifier.encode('utf-8')
                individual_store['created_on'] = str(cur_date).encode('utf-8')

    def __verify_credential(self, user_string):
        """Check validity of user string against hash"""
        p_hash = PasswordHasher()
        data = self.serialize_data(user_string)

        with dbm.open(self.__file_path, 'r') as individual_store:
            try:
                user_hash = individual_store.get("hash_string").decode("utf-8")
            except KeyError:
                return "User hash not found in the database."

            try:
                check_validity = p_hash.verify(user_hash, data)
            except argon2.exceptions.VerifyMismatchError:
                return "User string does not match the stored hash."

            if check_validity:
                return "Success"
            return None
    
    def verify_user(self, request_data):
        """Locate the DB file by UID and verify credentials."""
        p_hash = PasswordHasher()
        uid = request_data.get('uid')

        if not uid:
            return "UID not provided in the request."

        file_name = f"user_db_{uid}"
        file_path = os.path.join(self.__get_path, file_name)
        user_string = self.serialize_data(request_data)

        if os.path.exists(file_path):
            with dbm.open(file_path, 'r') as individual_store:
                try:
                    user_hash = individual_store.get("hash_string").decode("utf-8")
                except KeyError:
                    return "User hash not found in the database."

                try:
                    check_validity = p_hash.verify(user_hash, user_string)
                except argon2.exceptions.VerifyMismatchError:
                    return "User string does not match the stored hash."

                if check_validity:
                    return f"User authenticated successfully for UID: {uid}"
                
                return None
        else:
            return f"No database found for UID: {uid}"

    def display_user_db(self):
        """Display the contents of the user-specific database."""
        view_db = {}
        with dbm.open(self.__file_path, 'r') as individual_store:
            for key in individual_store.keys():
                try:
                    key_str = key.decode('utf-8')
                except UnicodeDecodeError:
                    key_str = key.hex()

                try:
                    value_str = individual_store[key].decode('utf-8')
                except UnicodeDecodeError:
                    value_str = individual_store[key].hex()

                view_db[key_str] = value_str
        return view_db

    @property
    def get_file_path(self):
        """Retrive store path"""
        return self.__file_path


    @property
    def get_file_name(self):
        """Retrive store file name"""
        return self.__file_name


    @property
    def get_uuid(self):
        """Retrive store id"""
        return self.__unique_identifier
