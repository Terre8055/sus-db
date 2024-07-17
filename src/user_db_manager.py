"""Module to store hashed user strings in database"""

import base64
import boto3
import datetime
import dbm
import json
import logging
import os
import uuid
from typing import (
    Dict,
    Union,
    Optional,
    
)
from logging.handlers import RotatingFileHandler
from botocore.exceptions import NoCredentialsError
import argon2
import shortuuid
from argon2 import PasswordHasher
from dotenv import load_dotenv

from settings import get_log_path, get_path
from user_path import UserPath



load_dotenv()


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def setExternalSupport() -> bool:
    """Check if external site support is enabled"""
    return os.getenv("SSDB_EXTERNAL_SUPPORT", "False").lower() == "true"

def setExternalLogPath(url: Union[str, os.PathLike]) -> Union[str, os.PathLike]:
    """Set the external file path
    eg: s3://bucket-name/logfileName
    If s3, bucket name should be valid and exists already
    """
    return url

def setExternalFilePath(url: Union[str, os.PathLike]) -> Union[str, os.PathLike]:
    """Set the external file path
    eg: s3://bucket-name/ 
    If s3, bucket name should be valid and exists already
    """
    return url

# Initialize the external paths if external support is enabled
external_support = setExternalSupport()
log_path = setExternalLogPath() if external_support else get_log_path
file_path_base = setExternalFilePath() if external_support else get_path

if log_path is not None:
    handler = RotatingFileHandler(log_path, maxBytes=10240, backupCount=5)
else:
    raise TypeError('Bad log path expression given')

handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(message)s', '%m/%d/%Y %I:%M:%S %p')
handler.setFormatter(formatter)
logger.addHandler(handler)


class UserDBManager:
    """Main DB Manager for IRs.

    This class manages user-specific databases, allowing for the storage and retrieval
    of hashed and secured user strings.
    """
    

    def __init__(self, uid: Optional[str] = None) -> None:
        """Initialize the user storage instance
        with a unique identifier attached to file name."""
        self.__get_path = file_path_base
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
    

    def db_file_exists(self) -> bool:
        """Check if a DBM file already exists with the given file path and name."""
        if external_support:
            s3_client = boto3.client('s3')
            bucket_name = self.__get_path.split('/')[2]  # Assuming 's3://bucket_name/' format
            key_name = '/'.join(self.__file_path.split('/')[3:])
            try:
                s3_client.head_object(Bucket=bucket_name, Key=key_name)
                return True
            except NoCredentialsError:
                logger.error("No AWS credentials found.")
                return False
            except s3_client.exceptions.ClientError:
                return False
        else:
            return os.path.exists(self.__file_path)
    
    def initialize_db(self) -> None:
        """Initialize the user-specific database if it doesn't exist."""
        if external_support:
            logger.info("External support enabled. Initializing database in S3.")
            self.__initialize_user_db_s3()
        else:
            os.makedirs(self.__get_path, exist_ok=True)
            with open(self.__file_path, 'w', encoding="utf-8"):
                pass
            self.__initialize_user_db()
        logger.info("UserDBManager instance initialized.")
        

    def __initialize_user_db(self) -> None:
        """Initialize the keys in the user-specific database"""
        with dbm.open(self.__file_path, 'n') as individual_store:
            individual_store['_id'] = b''
            individual_store['hash_string'] = b''
            individual_store['secured_user_string'] = b''
            individual_store['created_on'] = b''


    def __initialize_user_db_s3(self) -> None:
        """Initialize the keys in the user-specific database in S3."""
        s3_client = boto3.client('s3')
        bucket_name = self.__get_path.split('/')[2]
        key_name = '/'.join(self.__file_path.split('/')[3:])
        
        # Creating an empty DBM file and uploading to S3
        with dbm.open(self.__file_path, 'n') as individual_store:
            individual_store['_id'] = b''
            individual_store['hash_string'] = b''
            individual_store['secured_user_string'] = b''
            individual_store['created_on'] = b''
        
        # with open(self.__file_path, 'rb') as file_data:
        #     s3_client.upload_fileobj(file_data, bucket_name, key_name)


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


    def store_user_string(
            self,
            req: Dict[str, str]) \
            -> Dict[str, str] | None:
        """Store user string after encryption and generate
        secure user string using uuid and shortuuid helper\
        encoding
        """
        for key in req.keys():
            if not req.get(key):
                logger.error(f"[STORAGE] Empty request received")
                return None
        serialised_data = self.serialize_data(req)
        user_hash = self.hash_user_string(serialised_data)
        uid: dict = {}

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
                secured_user_string = self.generate_secured_string().encode('utf-8')
                individual_store['secured_user_string'] = secured_user_string
                individual_store['_id'] = self.__unique_identifier.encode(
                    'utf-8')
                individual_store['created_on'] = str(
                    current_date).encode('utf-8')

            user_id = individual_store.get('_id')
            
            if user_id:
                uid.update(id = user_id.decode('utf-8'))
                logger.info("[STORAGE] UserID successfully assigned...")
            else:
                logger.error("[STORAGE] User ID is None. Unable to assign to uid")
                raise TypeError("User ID is None. Unable to assign to 'uid'.")
            
            if external_support:
                s3_client = boto3.client('s3')
                bucket_name = self.__get_path.split('/')[2]
                key_name = '/'.join(self.__file_path.split('/')[3:])
                
                with open(self.__file_path, 'rb') as file_data:
                    s3_client.upload_fileobj(file_data, bucket_name, key_name)

        return uid

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
                    logger.error(f"[VERIF] User string does not match the stored hash for UID: {user_id}.")
                    return "User string does not match the stored hash."

                if check_validity:
                    logger.info(f"[VERIF] User verification successful for UID: {user_id}.")
                    return "Success"
                
                logger.warning(f"[VERIF] User verification failed for UID: {user_id}.")
                return None
        else:
            logger.error(f"[VERIF] No database found for UID: {user_id}")
            return f"No database found for UID: {user_id}"

    def display_user_db(self, user_id: str) \
            -> str | Dict[str | bytes, str]:
        """Display the contents of the user-specific database

        Returns:
            Dict[str | bytes, str]:  A dictionary containing the database contents.
        """
        view_database = {}
        file_name = f"user_db_{user_id}"
        file_path = os.path.join(self.__get_path, file_name)
        
        if os.path.exists(file_path):
            with dbm.open(file_path, 'r') as individual_store:
                for key in individual_store.keys():
                    try:
                        view_database[key] = individual_store[key].decode('utf-8')
                    except UnicodeDecodeError:
                        view_database[key] = individual_store[key].hex()

                    return view_database
                
        logger.error(f"[DISPLAY] No database founD for UID: {user_id}")
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

    def recover_account(self, req: Dict[str, str]) -> Union[Dict[str, str], str]:
        """Method to recover account with id and user string

        Args:
            req (Dict[str, str]): Request data passed as a dict
        """
        response_data: Dict[str, str] = {}
        
        get_uid = req.get('_id')
        if not get_uid:
            raise ValueError('No value received for id')

        user_string = req.get('user_string')
        if not user_string:
            raise ValueError('No value for user_string')

        serialised_string = self.serialize_data({'request_string': user_string})

        file_name = f"user_db_{get_uid}"
        file_path = os.path.join(self.__get_path, file_name)
        
        if os.path.exists(file_path):
            logger.info(f'[RECOVER] File for user: {get_uid} exists.')
            with dbm.open(file_path, 'w') as individual_store:
                logger.info(f'[RECOVER] Initiating File recovery for user: {get_uid}')
                try:
                    hashed_string = self.hash_user_string(serialised_string)
                    if hashed_string:
                        individual_store['hash_string'] = hashed_string.encode('utf-8')
                        logger.info(f"[RECOVER] String hashed successfully for file: {get_uid}")
                    hash_string_bytes = individual_store.get('hash_string')
                    if hash_string_bytes is not None:
                        secure_user_string = self.generate_secured_string().encode("utf-8")
                        individual_store['secured_user_string'] = secure_user_string
                        response_data.update(_id=get_uid, sus=secure_user_string)
                        logger.info(f"[RECOVER] Recovery completed, sus assigned")
                        return response_data
                except Exception as e:
                    logger.error(f"[RECOVER] {e}", exc_info=True)

        logger.error(f"[RECOVER] DBM not found for user: {get_uid}")
        return "DBM not found"
    
    
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
        
        if os.path.exists(file_path):
            try:
                with dbm.open(file_path, 'r') as individual_store:
                    db_secured = individual_store.get('secured_user_string')
                    if db_secured is None:
                        logger.error(f"[CLOSE ACCOUNT]  Account does not exist for UID: {user_id}")
                        return 'User not found'
                    check_integrity = db_secured.decode('utf-8') == secured_user_string
                    if not check_integrity:
                        return 'Provided Secured User String does not match for UID'
                    os.remove(file_path)
                    if os.path.exists(file_path):
                        logger.warning(f"[CLOSE ACCOUNT] DBM file not deleted")
                        return 'Error' 
                    logger.info(f"[CLOSE ACCOUNT] Account deleted successfully for UID: {user_id}")
                    return 'Success'
            except Exception as e:
                logger.error(f"[CLOSE ACCOUNT] {e}", exc_info=True)
                return 'Error deleting account'
     
        logger.error(f"[CLOSE ACCOUNT] DBM not found for user: {user_id}")
        return 'DBM not found'    
