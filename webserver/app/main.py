import argparse
import os
import socket
import threading

parser = argparse.ArgumentParser(description='build my own web server')
parser.add_argument('--host', help='host of web server', default='127.0.0.1')
parser.add_argument('--port', help='port of web server', default='3300')
args = parser.parse_args()

HOST = args.host
PORT = int(args.port)

print(HOST, PORT)


def _handle_request_thread(conn: socket.socket):
    with conn:
        data = conn.recv(1024)
        if not data:
            return
        data = data.decode().split('\n')
        request_info = data[0].split()
        path = request_info[1]
        print(f'Requested path: {path}')
        print(f'Thread: {threading.current_thread().name}')
        file_name = 'www/index.html' if path == '/' else f'www{path}'
        if path == '/' or os.path.isfile(file_name):
            with open(file_name, 'r') as file:
                content = file.read()
            response = f'HTTP/1.1 200 OK\r\n\r\n{content}\r\n'
        else:
            response = 'HTTP/1.1 404 Not Found'
        response = response.encode()
        conn.send(response)


def run():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f'running web server on port {PORT}')
        s.bind((HOST, PORT))
        s.listen(100)
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=_handle_request_thread, args=(conn, ))
            t.start()


if __name__ == '__main__':
    run()
