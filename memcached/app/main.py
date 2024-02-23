import argparse
import socket
import sys
import threading

from app.memcache import Memcache

parser = argparse.ArgumentParser(description='arguments for memcached server')
parser.add_argument('-p', help='memcached port number', default=11211, type=int)
args = parser.parse_args()

HOST = '127.0.0.1'
PORT = int(args.p)
two_parts_data = ('add', 'append', 'cas', 'prepend', 'replace', 'set')


def _request(conn: socket.socket):
    with conn:
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    return

                data = data.decode().split('\r\n')
                data = data[0].split()
                if data[0] == 'exit':
                    return

                if data and data[0] in two_parts_data:
                    value = conn.recv(1024)
                    value = value.decode().split('\r\n')
                    value = value[0].split()
                    data.extend(value)

                memcache = Memcache()
                response = memcache.run_command(*data)
                if response:
                    if not response.endswith('\r\n'):
                        response += '\r\n'
                    conn.send(response.encode())
            except (KeyboardInterrupt, UnicodeDecodeError):
                return


def run():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print(f'running memcached on {HOST}:{PORT} ...')
            s.bind((HOST, PORT))
            s.listen(10)
            while True:
                connection, _ = s.accept()
                t = threading.Thread(target=_request, args=(connection,))
                t.start()
    except KeyboardInterrupt:
        sys.exit()


if __name__ == '__main__':
    run()
