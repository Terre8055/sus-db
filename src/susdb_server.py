from flask import Flask, request, jsonify
from user_db_manager import UserDBManager
import argon2

app = Flask(__name__)

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

@app.route('/store', methods=['POST'])
def store_user_string():
    data = get_request_data()
    user_string = data.get('req')
    req = {'request_string': user_string}
    uid = UserDBManager().store_user_string(req).get('id')
    return jsonify({'uid': uid})

@app.route('/verify', methods=['POST'])
def verify_user():
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

@app.route('/view', methods=['POST'])
def display_user_db():
    data = get_request_data()
    uid = data.get('uid')
    user_db_view = UserDBManager(uid).display_user_db(uid)
    return jsonify({'db_view': user_db_view})

@app.route('/retrieve', methods=['POST'])
def deserialize_data():
    data = get_request_data()
    uid = data.get('uid')
    user_key = data.get('key')
    user_data = UserDBManager(uid).deserialize_data(uid, user_key)
    return jsonify({'user_data': user_data})

@app.route('/close', methods=['POST'])
def remove_user_account():
    data = get_request_data()
    uid = data.get('uid')
    secured_user_string = data.get('sus')
    req = {'uid': uid, 'sus': secured_user_string}
    response = UserDBManager(uid).close_account(req)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True, port=8000)
