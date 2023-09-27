"""Module to hash user strings and retrive secure user strings"""

import os
import dbm
import hashlib
import json
import hmac
import uuid
import base64
from hmac import compare_digest as cdg
from dotenv import load_dotenv
import bcrypt

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
        with dbm.open(self.file_path, 'n') as db:
            db['_id'] = b''
            db['hash_sus'] = b''
            db['stored_hmac'] = b''
            db['bhash'] = b''

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
        return hashlib.sha256(user_str_bytes).hexdigest()

    def generate_secured_user_string(self, request_data):
        """Generate the secured user string using a series of hashing and encryption."""
        # Serialize request data to JSON
        request_json = self.serialize_data(request_data)



        # Hash the serialized user string
        test_hash = self.hash_user_string(request_json)



        with dbm.open(self.file_path, 'w') as db:
            db['hash_sus'] = test_hash.encode('utf-8)')

            computed_hmac = hmac.new(
                self.secret_key,
                test_hash.encode('utf-8'),
                hashlib.sha256).digest()

            db['stored_hmac'] = computed_hmac

            stored_hmac = db.get('stored_hmac', None)
            get_hs = db.get('hash_sus')

            # Verify the HMAC to ensure integrity and authenticity
            get_integrity =  stored_hmac and cdg(stored_hmac, computed_hmac)

            if get_integrity:
                # if integrity of crypt rep is achieved, add second hash layer
                # and extract secured string with b64
                b_hash = bcrypt.hashpw(get_hs, bcrypt.gensalt())
                print('bcrypt: ->',  b_hash)
                if bcrypt.checkpw(get_hs, b_hash):
                    print("Worked")
                    db['bhash'] = b_hash

                secure_username = base64.urlsafe_b64encode(b_hash).decode('utf-8')[12:24]
                db['secured_user_string'] = secure_username
                db['_id'] = self.unique_identifier.encode('utf-8')

    def display_user_db(self):
        """Display the contents of the user-specific database."""
        with dbm.open(self.file_path, 'r') as db:
            for key in db.keys():
                try:
                    key_str = key.decode('utf-8')
                except UnicodeDecodeError:
                    key_str = key.hex()

                try:
                    value_str = db[key].decode('utf-8')
                except UnicodeDecodeError:
                    value_str = db[key].hex()

                print(f"Key: {key_str}, Value: {value_str}")
