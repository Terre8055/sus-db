#!/usr/bin/env python3

import dbm
import os
import hashlib
from dotenv import load_dotenv
import hmac
from hmac import compare_digest as cdg
import bcrypt
import base64

load_dotenv()

# Secret key for HMAC verification
secret_key = os.getenv("HMAC_SECRET_KEY").encode('utf-8')

# Function to hash the user string
def HashString(user_str=None):
    user_str_bytes = user_str.encode('utf-8')
    return hashlib.sha256(user_str_bytes).hexdigest()


# test string
request_str = 'bxgtef784po0' 

# Hash the user string
test_hash = HashString(request_str)

FILE_NAME = os.getenv("FILE_NAME")
GET_PATH = os.getenv("GET_PATH")
file_path = os.path.expanduser(f'~/{GET_PATH}/{FILE_NAME}')

if os.path.exists(file_path):
    with dbm.open(file_path, 'ns') as db:
        db['hash_sus'] = test_hash
        print('hashlib: ->', db.get('hash_sus'))

        get_hs = db.get('hash_sus')

        # Compute the HMAC of the stored hash 
        # computed_hmac is a crypto rep of the hash
        computed_hmac = hmac.new(secret_key, test_hash.encode('utf-8'), hashlib.sha256).digest()
        db['stored_hmac'] = computed_hmac
        
        stored_hmac = db.get('stored_hmac', None)

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

print('<---------------------------------------------------------------------------->')
print('<---------------------------------------------------------------------------->')
print('<---------------------------------------------------------------------------->')
print('<---------------------------------------------------------------------------->')
print('<---------------------------------------------------------------------------->')


with dbm.open(file_path, 'r') as db:
    # Iterate through all the keys
    for key in db.keys():
        value = db[key]  # Retrieve the value for each key
        print(f"Key: {key.decode()}, Value: {value.decode()}")  # Decode bytes to string for display
