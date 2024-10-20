"""Module to store hashed user strings in database"""

import base64
import datetime
import dbm
import json
import logging
import os
import uuid
from typing import (
    Dict,
    Union,
    Optional
)
from logging.handlers import RotatingFileHandler
import argon2
import shortuuid
from argon2 import PasswordHasher
from dotenv import load_dotenv

from settings import get_log_path, get_path

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_path = get_log_path 
if log_path is not None:
    handler = RotatingFileHandler(
        log_path,
        maxBytes=10240,
        backupCount=5
    )
else:
    raise TypeError('Bad log path expression given')
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s - %(message)s',
    '%m/%d/%Y %I:%M:%S %p'
)
handler.setFormatter(formatter)


logger.addHandler(handler)


class UserDBManager:
    """Main DB Manager for IRs.

    This class manages user-specific databases, allowing for the storage and retrieval
    of hashed and secured user strings.
    """
    
    def db_file_exists(self) -> bool:
        """Check if a DBM file already exists with the given file path and name."""
        return os.path.exists(self.get_file_path)

    def __init__(self, uid: Optional[str] = None) -> None:
        """Initialize the user storage instance
        with a unique identifier attached to file name."""
        self.__get_path = os.path.expanduser(get_path) if get_path else ''
        self.__unique_identifier = uid if uid else str(uuid.uuid4()) #Except for storing strings, always pass in the uid
        self.__file_name = f"user_db_{self.__unique_identifier}"
        self.__file_path = os.path.join(self.__get_path, self.__file_name)
        
        if self.db_file_exists():
            logger.info(f"[INIT] UserDBManager instance already exists for {self.get_file_name}, skipping initialisation.")
            return
        else:
            self.initialize_db()
            logger.info(f"[INIT] UserDBManager instance initialized for {self.get_file_name}.")

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
    
    def initialize_db(self) -> None:
        """Initialize the user-specific database if it doesn't exist.
        Ensure the directory exists or create it
        Creates an empty file named 'user_db<uid>' inside the directory
        """
            
        os.makedirs(self.__get_path, exist_ok=True)

        with open(self.__file_path, 'w', encoding="utf-8"):
            pass

        self.__initialize_user_db()
        logger.info("UserDBManager instance initialised.")

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

    def _fetch_user_data(self, uid: str, key: str) -> Optional[Union[str, bytes]]:
        """Fetch specific user data from the database.

        Args:
            key (str): The key to fetch the data.

        Returns:
            Optional[Union[str, bytes]]: The data associated with the key, or None
        """
        file_name = f"user_db_{uid}"
        file_path = os.path.join(self.__get_path, file_name)
        if os.path.exists(file_path):
            with dbm.open(file_path, 'r') as individual_store:
                user_data_bytes = individual_store.get(key.encode('utf-8'))
                if user_data_bytes is not None:
                    logger.info(f"[FETCH] Data fetched from file: {file_name} ")
                    return user_data_bytes.decode('utf-8')
                logger.warning(f'[FETCH] Associated key not found in file: {file_name}')
                return f"Associated key not found"
        logger.error("[FETCH] System Error while key lookup")
        return f'System Error while fetching'

    def deserialize_data(self, uid: str, key: str) -> Optional[Union[str, bytes]]:
        """Fetch and deserialize user data from the database using a specific key.

        Args:
            uid: user id
            key (str): The key to fetch and deserialize data.

        Returns:
            Optional[Union[str, bytes]]: The deserialized data associated with the key
        """
        user_id = uid
        user_data = self._fetch_user_data(user_id, key)
        return user_data

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

    def generate_secured_string(self) -> str:
        """Method to generate secured user string 
        using the global uuid and shortuuid module
        """
        unique_id = uuid.uuid4()
        secure_user_string = shortuuid.encode(unique_id)
        return secure_user_string


    def store_user_string(self, req: Dict[str, str]) -> Optional[Dict[str, str]]:
        """
        Store user string after encryption and generate secure user string.

        Args:
            req (Dict[str, str]): The request containing the user string.

        Returns:
            Optional[Dict[str, str]]: A dictionary containing the user ID if successful, None otherwise.
        """
        # Validate input
        if not all(req.values()):
            logger.error("[STORAGE] Empty request received")
            return None

        serialised_data = self.serialize_data(req)
        user_hash = self.hash_user_string(serialised_data)

        with dbm.open(self.__file_path, 'c') as individual_store:
            individual_store['hash_string'] = user_hash
            
            current_datetime = datetime.datetime.now().isoformat()
            secured_user_string = self.generate_secured_string()

            individual_store['secured_user_string'] = secured_user_string
            individual_store['_id'] = self.__unique_identifier
            individual_store['created_on'] = current_datetime

            user_id = individual_store.get('_id')
            
            if user_id:
                logger.info("[STORAGE] UserID successfully assigned")
                return {"id": user_id.decode('utf-8') }
            else:
                logger.error("[STORAGE] User ID is None. Unable to assign to uid")
                return None

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

        user_string = self.serialize_data(req)

        # Use display_user_db to get the user data
        user_data = self.display_user_db(user_id)

        if isinstance(user_data, dict):
            try:
                user_hash = user_data.get("hash_string")
                if user_hash is None:
                    return "User hash not found in the database."

                try:
                    check_validity = passwd_hash.verify(user_hash, user_string)
                except argon2.exceptions.VerifyMismatchError:
                    logger.error(f"[VERIF] User string does not match the stored hash for UID: {user_id}.")
                    return "User string does not match the stored hash."

                if check_validity:
                    logger.info(f"[VERIF] User verification successful for UID: {user_id}.")
                    return "Successful"
                
                logger.warning(f"[VERIF] User verification failed for UID: {user_id}.")
                return None
            except Exception as e:
                logger.error(f"[VERIF] Error during verification for UID: {user_id}. Error: {str(e)}")
                return f"Error during verification: {str(e)}"
        else:
            # If user_data is a string, it means no database was found
            logger.error(f"[VERIF] {user_data}")
            return user_data

    def display_user_db(self, user_id: str) -> Union[str, Dict[str, str]]:
        """Display the contents of the user-specific database

        Args:
            user_id (str): The user ID to look up the database for.

        Returns:
            Union[str, Dict[str, str]]: A dictionary containing the database contents,
            or an error message if the database is not found.
        """
        view_database: Dict[str, str] = {}
        file_name = f"user_db_{user_id}"
        file_path = os.path.join(self.__get_path, file_name)
        
        if os.path.exists(file_path):
            with dbm.open(file_path, 'r') as individual_store:
                for key in individual_store.keys():
                    try:
                        view_database[key.decode('utf-8')] = individual_store[key].decode('utf-8')
                    except UnicodeDecodeError:
                        view_database[key.decode('utf-8')] = individual_store[key].hex()
            
            logger.info(f"[DISPLAY] Database contents retrieved for UID: {user_id}")
            return view_database
                
        logger.error(f"[DISPLAY] No database found for UID: {user_id}")
        return f"No database found for UID: {user_id}"

    def check_sus_integrity(self, req: Dict[str, str]) -> str:
        """Check secured user strings integrity before restoring dbm

        Args:
            req (Dict[str, str]): Request data passed as a dict

        Raises:
            TypeError: If values in dict is None

        Returns:
            str: `Success` if integrity check passes
        """
        get_user_id, get_secured_user_string \
            = req.get('uid'), req.get('secured_user_string')
        if not get_user_id and not get_secured_user_string :
            raise TypeError("Invalid key passed")
        file_name = f"user_db_{get_user_id}"
        file_path = os.path.join(self.__get_path, file_name)
        if os.path.exists(file_path):
            logger.info(f'[RESTORE] File for user: {get_user_id} exists.')
            with dbm.open(file_path, 'r') as individual_store:
                try:
                    find_secure_user_string = individual_store.get(
                        "secured_user_string")
                    if find_secure_user_string is not None:
                        check_string_integrity = \
                            find_secure_user_string.decode('utf-8') \
                            == get_secured_user_string
                        if check_string_integrity:
                            logger.info(f"[RESTORE] Integrity check passed for user:{get_user_id}")
                            return "Success"
                        logger.warning(f"[RESTORE] Integrity check failed for user:{get_user_id}")
                        return "Error, Integrity check failed"
                except KeyError:
                    return "User string not found in the database."
        logger.error(f"[RESTORE] DBM not found for user: {get_user_id}")
        return f"DBM not found"

    def recover_account(self, req: Dict[str, str]) -> Optional[Dict[str, str]]:
        """
        Recover an account with id and user string.

        Args:
            req (Dict[str, str]): Request data containing '_id' and 'user_string'.

        Returns:
            Optional[Dict[str, str]]: A dictionary containing the user ID and secured user string if successful, None otherwise.
        """
        get_uid = req.get('_id')
        user_string = req.get('user_string')

        if not get_uid or not user_string:
            logger.error("[RECOVER] Missing '_id' or 'user_string' in request")
            return None

        file_name = f"user_db_{get_uid}"
        file_path = os.path.join(self.__get_path, file_name)
        
        if not os.path.exists(file_path):
            logger.error(f"[RECOVER] DBM not found for user: {get_uid}")
            return None

        serialized_data = self.serialize_data({'request_string': user_string})
        user_hash = self.hash_user_string(serialized_data)

        with dbm.open(file_path, 'c') as individual_store:
            individual_store['hash_string'] = user_hash
            
            current_datetime = datetime.datetime.now().isoformat()
            secured_user_string = self.generate_secured_string()

            individual_store['secured_user_string'] = secured_user_string
            individual_store['_id'] = get_uid
            individual_store['created_on'] = current_datetime

            logger.info(f"[RECOVER] Account recovered successfully for user: {get_uid}")
            return {
                "id": get_uid,
                "sus": secured_user_string
            }
    
    
    def close_account(self, req: Dict[str, str]) -> str:
        """Method to support permanent account deletion

        Args:
            req (Dict): request param (uid, secured user string)

        Raises:
            KeyError: KeyError when empty queries are passed in

        Returns:
            str: Success if successful 
        """
        user_id = req.get('uid')
        secured_user_string = req.get('sus')
        if not user_id or not secured_user_string:
            raise KeyError('Error parsing user input')
        
        file_name = f"user_db_{user_id}"
        file_path = os.path.join(self.__get_path, file_name)
        
        if not os.path.exists(file_path):
            logger.error(f"[CLOSE ACCOUNT] DBM not found for user: {user_id}")
            return 'DBM not found'

        try:
            with dbm.open(file_path, 'r') as individual_store:
                db_secured = individual_store.get('secured_user_string')
                if db_secured is None:
                    logger.error(f"[CLOSE ACCOUNT] Account does not exist for UID: {user_id}")
                    return 'User not found'
                if db_secured.decode('utf-8') != secured_user_string:
                    logger.warning(f"[CLOSE ACCOUNT] Provided Secured User String does not match for UID: {user_id}")
                    return 'Provided Secured User String does not match for UID'
            
            os.remove(file_path)
            if os.path.exists(file_path):
                logger.error(f"[CLOSE ACCOUNT] Failed to delete DBM file for UID: {user_id}")
                return 'Error: Failed to delete account'
            
            logger.info(f"[CLOSE ACCOUNT] Account deleted successfully for UID: {user_id}")
            return 'Success'
        except Exception as e:
            logger.error(f"[CLOSE ACCOUNT] Error deleting account for UID: {user_id}. Error: {str(e)}", exc_info=True)
            return 'Error deleting account'




