import argparse
import socket
import sys

parser = argparse.ArgumentParser(description='arguments for redis client')
parser.add_argument('commands', help='cli commands', nargs='*')
parser.add_argument('-p', help='redis server port', default=6379, type=int)
args = parser.parse_args()

PORT = int(args.p)
HOST = '127.0.0.1'
SPLIT_CHAR = ' )^%*#@$!( '


def run():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print(f'connected to redis server {HOST}:{PORT}')
            s.connect((HOST, PORT))
            message = SPLIT_CHAR.join(args.commands)
            # print('===')
            # print(message)
            # print('===')
            s.send(message.encode('utf-8'))
            data = s.recv(1024)
            print(data.decode('utf-8'))
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    run()
    # print(args.commands)
