import http.server
import socketserver
import json
from user_db_manager import UserDBManager
import argon2
from urllib.parse import urlparse, parse_qs

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class SusDBHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # Parse URL and query parameters
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)

        # Combine POST data and query parameters
        data = json.loads(post_data.decode('utf-8')) if post_data else {}
        data.update({k: v[0] for k, v in query.items()})

        response = {}
        match path:
            case '/store':
                response = self.store_user_string(data)
            case '/verify':
                response = self.verify_user(data)
            case '/view':
                response = self.display_user_db(data)
            case '/retrieve':
                response = self.deserialize_data(data)
            case '/close':
                response = self.remove_user_account(data)
            case _:
                self.send_error(404, "Endpoint not found")
                return

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def store_user_string(self, data):
        user_string = data.get('req')
        req = {'request_string': user_string}
        uid = UserDBManager().store_user_string(req).get('id')
        return {'uid': uid}

    def verify_user(self, data):
        req = {
            'request_string': data.get('req'),
            'uid': data.get('uid')
          }
        msg = UserDBManager(uid=data.get('uid')).verify_user(req)
        
        if msg != "Success":
            msg = "failed"
        return {'status': msg}

    def display_user_db(self, data):
        uid = data.get('req')
        req = {'id': uid}
        uid = UserDBManager().display_user_db(req).get('id')
        return {'uid': uid}

    def deserialize_data(self, data):
        uid = data.get('req')
        req = {'id': uid}
        uid = UserDBManager().deserialize_data(req).get('id')
        return {'uid': uid}

    def remove_user_account(self, data):
        uid = data.get('req')
        req = {'id': uid}
        uid = UserDBManager().remove_user_account(req).get('id')
        return {'uid': uid}


def run_server(port=8000):
    with socketserver.TCPServer(("", port), SusDBHandler) as httpd:
        print(f"Serving SusDB at port {port}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()