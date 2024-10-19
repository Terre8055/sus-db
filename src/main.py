from flask import Flask, request, jsonify
from user_db_manager import UserDBManager
import argon2
import logging
from urls import *
app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_request_data():
    """Combine JSON, form, and query string data from the request."""
    data = {}
    # Get JSON data
    if request.is_json:
        data.update(request.get_json())
    # Get form data
    data.update(request.form.to_dict())
    # Get query string arguments
    data.update(request.args.to_dict())
    return data

@app.route(STORE, methods=['POST'])
def store_user_string():
    """
    Store a user string in the database.

    This endpoint expects a POST request with a 'req' parameter containing the user string.
    It stores the user string in the database and returns a unique identifier (UID) for the stored data.

    Returns:
        A JSON object containing the 'uid' of the stored user string.
    """
    data = get_request_data()
    user_string = data.get('req')
    req = {'request_string': user_string}
    uid = UserDBManager().store_user_string(req).get('id')
    return jsonify({'uid': uid})

@app.route(VERIFY, methods=['POST'])
def verify_user():
    """
    Verify a user's string in the database.

    This endpoint expects a POST request with a 'string' and 'uid' parameter.
    It verifies the user's string in the database and returns a message indicating the result.

    Returns:
        A JSON object containing the 'status' of the verification process.
    """
    data = get_request_data()
    req = {
        'request_string': data.get('string'),
        'uid': data.get('uid')
    }
    try:
        msg = UserDBManager(uid=data.get('uid')).verify_user(req)
        return jsonify({'status': msg})
    except argon2.exceptions.InvalidHashError:
        return jsonify({'error': 'Invalid parameters passed, Check uid or string'}), 400

@app.route(VIEW, methods=['POST'])
def display_user_db():
    """
    Display the user database.

    This endpoint expects a POST request with a 'uid' parameter.
    It displays the user database and returns the view.

    Returns:
        A JSON object containing the 'db_view' of the user database.
    """
    data = get_request_data()
    uid = data.get('uid')
    user_db_view = UserDBManager(uid).display_user_db(uid)
    sanitized_db_view = {str(k): v for k, v in user_db_view.items()}
    return jsonify({'db_view': sanitized_db_view})

@app.route(RETRIEVE, methods=['POST'])
def deserialize_data():
    """
    Deserialize user data from the database.

    This endpoint expects a POST request with a 'uid' and 'key' parameter.
    It deserializes the user data from the database and returns the data.

    Returns:
        A JSON object containing the 'user_data' of the user database.
    """
    data = get_request_data()
    uid = data.get('uid')
    user_key = data.get('key')
    user_data = UserDBManager(uid).deserialize_data(uid, user_key)
    return jsonify({'user_data': user_data})

@app.route(CLOSE, methods=['POST'])
def remove_user_account():
    """
    Remove a user's account from the database.

    This endpoint expects a POST request with a 'uid' and 'sus' parameter.
    It removes the user's account from the database and returns a response.

    Returns:
        A JSON object containing the 'response' of the account removal process.
    """
    data = get_request_data()
    uid = data.get('uid')
    secured_user_string = data.get('sus')
    req = {'uid': uid, 'sus': secured_user_string}
    response = UserDBManager(uid).close_account(req)
    return jsonify({'response': response})

@app.route(RECOVER, methods=['POST'])
def recover_account():
    """
    Recover a user's account from the database.

    This endpoint expects a POST request with a 'uid' and 'user_string' parameter.
    It recovers the user's account from the database and returns a response.

    Returns:
        A JSON object containing the 'response' of the account recovery process.
    """
    data = get_request_data()
    uid = data.get('uid')
    user_string = data.get('user_string')
    req = {'_id': uid, 'user_string': user_string}
    response = UserDBManager(uid).recover_account(req)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(
        debug=False, 
        port=8000, 
        host='0.0.0.0', 
        load_dotenv=True
    )