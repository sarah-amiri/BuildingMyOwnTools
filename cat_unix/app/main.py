import argparse
import os
import sys

parser = argparse.ArgumentParser(description='building unix cat')
parser.add_argument('files', help='file names', nargs='*')
parser.add_argument('-n', help='print line number', action='store_true')
args = parser.parse_args()


def run():
    files = args.files
    if files:
        for file_path in files:
            if not os.path.isfile(file_path):
                print(f'{file_path}: No such file or directory')
                sys.exit(1)

            with open(file_path, 'rb') as file:
                lines = file.readlines()
            for number, content in enumerate(lines):
                print('{}{}'.format(str(number + 1).rjust(6) + '  ' if args.n else '', content.decode().strip()))
    else:
        counter = 1
        for line in sys.stdin:
            if args.n:
                print(str(counter).rjust(6), end='  ')
            print(line.strip())
            counter += 1


if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        sys.exit(0)
