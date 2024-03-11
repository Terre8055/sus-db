import socket
import json
from user_db_manager import UserDBManager

def handle_client(client_socket, user_db_manager):
    while True:
        data = client_socket.recv(1024).decode()
        if not data:
            break
        request = json.loads(data)
        # Example: Handle database commands
        if request['command'] == 'GET':
            key = request['key']
            value = user_db_manager.get(key)
            response = {'result': value}
            client_socket.send(json.dumps(response).encode())
        elif request['command'] == 'SET':
            key = request['key']
            value = request['value']
            user_db_manager.set(key, value)
            client_socket.send(b'OK')
        else:
            client_socket.send(b'Invalid command')
    client_socket.close()

def main():
    host = '0.0.0.0'  # Listen on all available interfaces
    port = 9999

    user_db_manager = UserDBManager()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Server listening on {host}:{port}")

    try:
        while True:
            client_socket, address = server_socket.accept()
            print(f"Accepted connection from {address[0]}:{address[1]}")
            handle_client(client_socket, user_db_manager)
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
