from dataclasses import dataclass
from enum import Enum
from typing import Union


@dataclass
class RedisObject:
    resp_value: str
    type: 'RedisType'
    value: Union


class RedisType(Enum):
    STRING = '+'
    ERROR = '-'
    INTEGER = ':'
    BULK_STRING = '$'
    ARRAY = '*'
    NULL = '$-1'

    sign_to_types = {
        '+': STRING,
        '-': ERROR,
        ':': INTEGER,
        '$': BULK_STRING,
        '*': ARRAY,
    }

    @classmethod
    def value_to_sign(cls, _input):
        if _input == '$-1\r\n':
            return cls.NULL
        if _input[0] in cls.sign_to_types:
            return cls.sign_to_types[_input[0]]
        raise Exception()

    @classmethod
    def input_to_type(cls, _input):
        if isinstance(_input, str):
            return cls.STRING.value
        if isinstance(_input, bytes):
            return cls.BULK_STRING.value
        if isinstance(_input, list):
            return cls.ARRAY.value
        if isinstance(_input, int):
            return cls.INTEGER.value
        raise Exception()
