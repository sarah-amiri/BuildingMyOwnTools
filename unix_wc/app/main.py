import argparse
from collections import defaultdict
import os
import sys
from typing import Dict, List

parser = argparse.ArgumentParser(description='script to build Unix wc tool with python')
parser.add_argument('filenames', help='Name of file', nargs='*')
parser.add_argument('-c', help='output number of bytes in a file', action='store_true')
parser.add_argument('--bytes', help='output number of bytes in a file', action='store_true')
parser.add_argument('-l', help='output number of lines in a file', action='store_true')
parser.add_argument('--lines', help='output number of lines in a file', action='store_true')
parser.add_argument('-w', help='output number of words in a file', action='store_true')
parser.add_argument('--words', help='output number of words in a file', action='store_true')
parser.add_argument('-m', help='output number of characters in a file', action='store_true')
parser.add_argument('--chars', help='output number of characters in a file', action='store_true')
args = parser.parse_args()


def _any_optional_argument_entered() -> bool:
    for arg in args.__dict__:
        if arg != 'filenames' and getattr(args, arg):
            return True
    return False


def extract_data(lines: List[str]) -> Dict[str, int]:
    lines_count = words_count = bytes_count = chars_count = 0
    for line in lines:
        lines_count += 1
        words_count += len(line.split())
        bytes_count += len(line)
        chars_count += len(line.decode())
    return {
        'lines_count': str(lines_count),
        'words_count': str(words_count),
        'bytes_count': str(bytes_count),
        'chars_count': str(chars_count),
    }


def print_outputs(outputs: Dict[str, str], max_numbers: Dict[str, int]) -> None:
    for output in outputs:
        if args.l or args.lines:
            print(output['lines_count'].rjust(max_numbers['lines_count']), end=' ')
        if args.w or args.words:
            print(output['words_count'].rjust(max_numbers['words_count']), end=' ')
        if args.m or args.chars:
            print(output['chars_count'].rjust(max_numbers['chars_count']), end=' ')
        if args.c or args.bytes:
            print(output['bytes_count'].rjust(max_numbers['bytes_count']), end=' ')

        if not _any_optional_argument_entered():
            print(f'{output["lines_count"].rjust(max_numbers["lines_count"])} '
                  f'{output["words_count"].rjust(max_numbers["words_count"])} '
                  f'{output["bytes_count"].rjust(max_numbers["bytes_count"])}', end=' ')

        if 'file_name' in output:
            print(output['file_name'].rjust(max_numbers['file_name']))
        else:
            print()


def run():
    file_names = args.filenames
    overall_counts = defaultdict(int)
    max_numbers = defaultdict(lambda: 0)
    outputs = []

    if not file_names:
        input_lines = [line.strip().encode('utf-8') for line in sys.stdin]
        if input_lines:
            outputs.append(extract_data(input_lines))
    else:
        for file_name in file_names:
            if not os.path.isfile(file_name):
                print(f'{file_name}: No such file or directory')
                exit()

            with open(file_name, 'rb') as file:
                output_data = extract_data(file.readlines())
            output_data['file_name'] = file_name
            outputs.append(output_data)

        if len(outputs) > 1:
            for output in outputs:
                for key, value in output.items():
                    if key != 'file_name':
                        overall_counts[key] = str(int(overall_counts[key]) + int(value))
                    if max_numbers[key] < len(value):
                        max_numbers[key] = len(value)
            overall_counts['file_name'] = 'total'
            outputs.append(overall_counts)

    print_outputs(outputs, max_numbers)


if __name__ == '__main__':
    run()
