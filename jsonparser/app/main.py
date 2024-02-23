import argparse
import sys
from typing import Dict, List, Optional, Union

parser = argparse.ArgumentParser(description='script to validate an input as json')
parser.add_argument('filename', help='Name of file to read input from', nargs='+')
args = parser.parse_args()


class JSONParser:
    def __init__(self, data: str):
        assert isinstance(data, str), 'Input data must be a string not a {}'.format(type(data))
        self.data = data
        self.__set_parser_type()

    def __set_parser_type(self) -> None:
        """
        This function sets parser type: 1 is for list and 2 is for dict
        :return: None
        """
        self.data = self.data.strip()
        if self.data[0][0] == '[' and self.data[-1][-1] == ']':
            self.parser_type = 1
        elif self.data[0][0] == '{' and self.data[-1][-1] == '}':
            self.parser_type = 2
        else:
            raise Exception()

    def _parse_string(self, input_data: str) -> Optional[str]:
        """
        This function parse input data as a string and return the parsed string if it is possible
        :param input_data: str
        :return: Optional[str]
        """
        if (isinstance(input_data, str) and len(input_data) >= 2 and
                input_data.startswith('"') and input_data.endswith('"')):
            return input_data[1:-1]
        return None

    def _parse_boolean(self, input_data: str) -> Optional[bool]:
        """
        This function parse input data as boolean and return the boolean if is it possible to parse it as a boolean
        :param input_data: str
        :return: Optional[bool]
        """
        if input_data == 'false':
            return False
        if input_data == 'true':
            return True
        return None

    def _is_null(self, input_data: str) -> None:
        return input_data == 'null'

    def _parse_number(self, input_data: str) -> Optional[Union[int, float]]:
        """
        This function parse input data as number and returns the parsed number if it can be parsed as a number
        :param input_data: str
        :return: Optional[Union[int, float]]
        """
        try:
            data = float(input_data)
        except (TypeError, ValueError):
            return None
        return int(data) if input_data.isdigit() else float(data)

    def _validate_key(self, key: str) -> str:
        parsed_key = self._parse_string(key)
        if not parsed_key:
            raise Exception()
        return parsed_key

    def _validate_value(self, value: str) -> Union[str, int, float, None, bool]:
        parsed_str = self._parse_string(value)
        if parsed_str:
            return parsed_str

        parsed_number = self._parse_number(value)
        if parsed_number:
            return parsed_number

        parsed_bool = self._parse_boolean(value)
        if parsed_bool is not None:
            return parsed_bool

        if self._is_null(value):
            return None

        parsed_dict = self._parse_dict(value)
        if parsed_dict is not None:
            return parsed_dict

        parsed_list = self._parse_list(value)
        if parsed_list is not None:
            return parsed_list

        raise Exception()

    def _parse_dict(self, value: str = None) -> Optional[Dict]:
        data = value or self.data
        if data[0] + data[-1] != '{}':
            return None

        data = data[1:-1]
        if data == '':
            return {}

        tokens = data.split(',')
        index = 0
        json_data = {}
        while index < len(tokens):
            token = tokens[index]
            token_split = ''.join(token.split())
            if ('{"' in token_split and '"}' not in token_split) or ('["' in token_split and '"]' not in token_split):
                for index_2 in range(index + 1, len(tokens)):
                    token_2 = tokens[index_2]
                    token_2_split = ''.join(token_2.split())
                    if ('{"' in token_split and '"}' in token_2_split) or ('["' in token_split and '"]' in token_2_split):
                        token = ','.join(tokens[index:index_2+1])
                        index = index_2
                        break
                    index_2 += 1
                else:
                    return None
            in_token = token.strip().split(':', maxsplit=1)
            if len(in_token) != 2:
                return None
            key, value = in_token
            key, value = key.strip(), value.strip()
            key = self._validate_key(key)
            val = self._validate_value(value)
            json_data[key] = val
            index += 1
        return json_data

    def _parse_list(self, value: str = None) -> Optional[List]:
        data = value or self.data
        if data[0] + data[-1] != '[]':
            return None

        data = data[1:-1]
        if data == '':
            return []

        tokens = data.split(',')
        index = 0
        json_data = []
        while index < len(tokens):
            token = tokens[index]
            token_split = ''.join(token.split())
            if ('{"' in token_split and '"}' not in token_split) or ('["' in token_split and '"]' not in token_split):
                for index_2 in range(index + 1, len(tokens)):
                    token_2 = tokens[index_2]
                    token_2_split = ''.join(token_2.split())
                    if ('{"' in token_split and '"}' in token_2_split) or ('["' in token_split and '"]' in token_2_split):
                        token = ','.join(tokens[index:index_2+1])
                        index = index_2
                        break
                    index_2 += 1
                else:
                    return None
            val = self._validate_value(token.strip())
            json_data.append(val)
            index += 1
        return json_data

    def parse(self) -> None:
        if self.parser_type == 1:
            parsed_data = self._parse_list()
        elif self.parser_type == 2:
            parsed_data = self._parse_dict()
        else:
            raise Exception()

        if parsed_data is None:
            raise Exception()


def validate_input(raw_data: str):
    json_parser = JSONParser(raw_data)
    try:
        json_parser.parse()
        print('input data is a valid json')
        sys.exit(0)
    except Exception as e:
        print(f'input data is not a valid json: {e}')
        sys.exit(1)


def run():
    try:
        with open(args.filename[0], 'r') as file:
            raw_data = file.read()
    except FileNotFoundError as err:
        print(str(err))
        sys.exit(1)
    else:
        validate_input(raw_data)


if __name__ == '__main__':
    run()
