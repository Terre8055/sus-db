import os
import dbm
import hashlib
from dotenv import load_dotenv
import hmac
from hmac import compare_digest as cdg
import bcrypt
import base64
import uuid

load_dotenv()

class UserDBManager:
    def __init__(self):
        """Initialize the SecureUserStorage instance."""
        self.secret_key = os.getenv("HMAC_SECRET_KEY").encode('utf-8')
        self.file_name = os.getenv("FILE_NAME")
        self.get_path = os.getenv("GET_PATH")
        self.file_path = os.path.expanduser(f'~/{self.get_path}/{self.file_name}')
        self.initialize_db()

    def initialize_db(self):
        """Initialize the user-specific database if it doesn't exist."""
        if not os.path.exists(self.file_path):
            os.makedirs(self.file_path)
            self._initialize_user_db()

    def _initialize_user_db(self):
        """Initialize the keys in the user-specific database."""
        with dbm.open(self.file_path, 'n') as db:
            db['uid'] = b''
            db['hash_sus'] = b''
            db['stored_hmac'] = b''
            db['bhash'] = b''

    def hash_user_string(self, user_str):
        """Hash the user string using SHA-256."""
        user_str_bytes = user_str.encode('utf-8')
        return hashlib.sha256(user_str_bytes).hexdigest()

    def generate_secured_user_string(self, request_str):
        """Generate the secured user string using a series of hashing and encryption."""
        test_hash = self.hash_user_string(request_str)

        with dbm.open(self.file_path, 'w') as db:
            db['hash_sus'] = test_hash

            computed_hmac = hmac.new(self.secret_key, test_hash.encode('utf-8'), hashlib.sha256).digest()
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

                secure_username = base64.urlsafe_b64encode(b_hash).decode('utf-8')[:12]
                db['secured_user_string'] = secure_username
                uid = str(uuid.uuid4())
                db['uid'] = uid.encode('utf-8')


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


