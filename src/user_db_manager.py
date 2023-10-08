"""Module to store hashed user strings in database"""

import base64
import datetime
import dbm
import json
import os
import uuid
from typing import (
    Dict,
    Union,
    Optional
)

import argon2
from argon2 import PasswordHasher
from dotenv import load_dotenv

from src.settings import get_path

load_dotenv()


class UserDBManager:
    """Main DB Manager for IRs.

    This class manages user-specific databases, allowing for the storage and retrieval
    of hashed and secured user strings.
    """

    def __init__(self) -> None:
        """Initialize the user storage instance
        with a unique identifier attached to file name."""
        self.__get_path = os.path.expanduser(get_path) if get_path else ''
        self.__unique_identifier = str(uuid.uuid4())
        self.__file_name = f"user_db_{self.__unique_identifier}"
        self.__file_path = os.path.join(self.__get_path, self.__file_name)
        self.initialize_db()

    def initialize_db(self) -> None:
        """Initialize the user-specific database if it doesn't exist.
        Ensure the directory exists or create it
        Creates an empty file named 'user_db<uid>' inside the directory
        """
        os.makedirs(self.__get_path, exist_ok=True)

        with open(self.__file_path, 'w', encoding="utf-8"):
            pass

        self.__initialize_user_db()

    def __initialize_user_db(self) -> None:
        """Initialize the keys in the user-specific database"""
        with dbm.open(self.__file_path, 'n') as individual_store:
            individual_store['_id'] = b''
            individual_store['hash_string'] = b''
            individual_store['secured_user_string'] = b''
            individual_store['created_on'] = b''

    def serialize_data(
            self,
            req: Dict[str, str]) \
            -> str:
        """Serialize incoming data to a JSON string.

        Raises:
            KeyError: Raises an error if `request_string` key not found

        Returns:
            str: A JSON string representing the serialized data
        """
        if 'request_string' in req:
            return json.dumps(req['request_string'])
        raise KeyError("Error parsing key")

    def deserialize_data(
            self,
            response_data: Union[str, bytes, bytearray]) \
            -> Dict[str, str]:
        """Deserialize a JSON string to the original data.

        Returns:
            Dict[str, str]: The original data represented as a dictionary.
        """
        return json.loads(response_data)

    def hash_user_string(
            self,
            user_string: str) \
            -> str:
        """Hash the user string using argon2

        Returns:
            str: The hashed user string.
        """
        user_string_bytes = user_string.encode('utf-8')
        passwd_hash = PasswordHasher()
        hashed_user_string = passwd_hash.hash(user_string_bytes)
        return hashed_user_string

    def store_user_string(
            self,
            req: Dict[str, str]) \
            -> None:
        """Store user string after encryption and generate
        secure user string using base64 encoding
        """
        serialised_data = self.serialize_data(req)
        user_hash = self.hash_user_string(serialised_data)

        with dbm.open(self.__file_path, 'w') as individual_store:
            individual_store['hash_string'] = user_hash.encode('utf-8)')
            hash_string = individual_store.get('hash_string')

            current_datetime = datetime.datetime.now()
            formatted_datetime = current_datetime.strftime(
                "%Y-%m-%dT%H:%M:%S.%f"
            )
            current_date = datetime.datetime.strptime(
                formatted_datetime, "%Y-%m-%dT%H:%M:%S.%f"
            )

            if hash_string is not None:
                secure_user_string = base64.urlsafe_b64encode(
                    hash_string
                ).decode('utf-8')[12:24]
                individual_store['secured_user_string'] = secure_user_string
                individual_store['_id'] = self.__unique_identifier.encode('utf-8')
                individual_store['created_on'] = str(current_date).encode('utf-8')

    def verify_user(
            self,
            req: Dict[str, str]) \
            -> Optional[str]:
        """ Locate the DB file by UID and verify user credentials.

        Returns:
            Optional[str]: A success message or None if verification fails.
        """
        passwd_hash = PasswordHasher()
        user_id = req.get('uid')

        if not user_id:
            return "UID not provided in the request."

        file_name = f"user_db_{user_id}"
        file_path = os.path.join(self.__get_path, file_name)
        user_string = self.serialize_data(req)

        if os.path.exists(file_path):
            with dbm.open(file_path, 'r') as individual_store:
                try:
                    user_hash_bytes = individual_store.get("hash_string")
                    if user_hash_bytes is not None:
                        user_hash = user_hash_bytes.decode('utf-8')
                except KeyError:
                    return "User hash not found in the database."

                try:
                    check_validity = passwd_hash.verify(user_hash, user_string)
                except argon2.exceptions.VerifyMismatchError:
                    return "User string does not match the stored hash."

                if check_validity:
                    return f"User authenticated successfully for UID: {user_id}"

                return None
        else:
            return f"No database found for UID: {user_id}"

    def display_user_db(self) \
            -> Dict[str | bytes, str]:
        """Display the contents of the user-specific database

        Returns:
            Dict[str | bytes, str]:  A dictionary containing the database contents.
        """
        view_database = {}
        with dbm.open(self.__file_path, 'r') as individual_store:
            for key in individual_store.keys():
                try:
                    view_database[key] = individual_store[key].decode('utf-8')
                except UnicodeDecodeError:
                    view_database[key] = individual_store[key].hex()

        return view_database

    @property
    def get_file_path(self) -> Union[str, os.PathLike]:
        """Retrieve store path"""
        return self.__file_path

    @property
    def get_file_name(self) -> str:
        """Retrieve store file name"""
        return self.__file_name

    @property
    def pk(self) -> str:
        """Retrieve store id"""
        return self.__unique_identifier
