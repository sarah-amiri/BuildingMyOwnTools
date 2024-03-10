import argparse
import socket
import sys
import threading

from serializers import process_data

parser = argparse.ArgumentParser(description='arguments for redis server')
parser.add_argument('-p', help='custom port number', default=6607, type=int)
args = parser.parse_args()

import random
HOST = '127.0.0.1'
PORT = int(random.randint(6000, 8000))


def _request(conn: socket.socket):
    with conn:
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    return

                message = process_data(data)
                conn.send(message)
            except (KeyboardInterrupt, UnicodeDecodeError):
                return


def run():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print(f'running redis server on {HOST}:{PORT}')
            s.bind((HOST, PORT))
            s.listen(100)
            while True:
                connection, _ = s.accept()
                t = threading.Thread(target=_request, args=(connection,))
                t.start()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    run()
    # value = '*5\r\n$6\r\nCONFIG\r\n$3\r\nGET\r\n*3\r\n$6\r\nCONFIG\r\n$3\r\nGET\r\n$10\r\nappendonly\r\n$3\r\nGET\r\n:100\r\n'
    # print(deserialize(value))
