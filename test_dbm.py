#!/usr/bin/env python3

import dbm
import os
import hashlib
from dotenv import load_dotenv
import hmac
from hmac import compare_digest as cdg

load_dotenv()

# Secret key for HMAC verification
secret_key = os.getenv("HMAC_SECRET_KEY").encode('utf-8')

# Function to hash the user string
def HashString(user_str=None):
    user_str_bytes = user_str.encode('utf-8')
    return hashlib.sha256(user_str_bytes).hexdigest()



request_str = 'bxgtef784po0'

# Hash the user string
test_hash = HashString(request_str)

FILE_NAME = os.getenv("FILE_NAME")
GET_PATH = os.getenv("GET_PATH")
file_path = os.path.expanduser(f'~/{GET_PATH}/{FILE_NAME}')

if os.path.exists(file_path):
    with dbm.open(file_path, 'ns') as db:
        db['secured_user_string'] = request_str
        db['hash_sus'] = test_hash

        # Compute the HMAC of the stored hash 
        # computed_hmac is a crypto rep of the hash
        computed_hmac = hmac.new(secret_key, test_hash.encode('utf-8'), hashlib.sha256).digest()
        db['stored_hmac'] = computed_hmac
        
        stored_hmac = db.get('stored_hmac', None)

        # Verify the HMAC to ensure integrity and authenticity
        get_integrity =  stored_hmac and cdg(stored_hmac, computed_hmac)

