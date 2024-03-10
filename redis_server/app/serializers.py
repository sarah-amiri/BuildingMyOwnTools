import datetime
import re
from threading import Lock
from typing import Dict, Union

from enums import RedisType
from structures import LinkedList

CRLF = '\r\n'
argument_error = 'wrong number of arguments for \'{}\' command'
expire_time_error = 'ERR invalid expire time in \'{}\' command'
syntax_error = 'ERR syntax error'
type_error = 'ERR value is not an integer or out of range'
unknown_error = 'ERR unknown command `{}`, with args beginning with: {}'
wrong_type_list_error = 'WRONGTYPE Operation against a key holding the wrong kind of value'
stored_data: Dict[str, Dict[str, Union[str, int]]] = {}
race_lock = Lock()


def serialize_string(value: str) -> str:
    return RedisType.STRING.value + value


def deserialize_string(value: str) -> str:
    try:
        return value[1:].split(CRLF)[0]
    except IndexError:
        return ''


def serialize_error(value: str) -> str:
    return RedisType.ERROR.value + value


def serialize_bytes(value: bytes) -> str:
    return RedisType.BULK_STRING.value + str(len(value)) + CRLF + value


def deserialize_bytes(value: str) -> str:
    return value[1:].split(CRLF)[1:-1][0]


def serialize_integer(value: int) -> str:
    return RedisType.INTEGER.value + str(value)


def deserialize_integer(value: str) -> int:
    return int(value[1:].split(CRLF)[0])


def serialize_array(value: list) -> str:
    result = CRLF.join([serialize(val, RedisType.BULK_STRING).decode('utf-8')[:-2] for val in value])
    return RedisType.ARRAY.value + str(len(value)) + CRLF + result


def deserialize_array(value: str) -> list:
    result = []
    if value == '*0\r\n\r\n':
        return result
    split_value = value[1:].split(CRLF)
    result_len = int(split_value[0])
    split_value = split_value[1:-1]
    index = 0
    while len(result) < result_len:
        if split_value[index].startswith('$'):
            val = split_value[index] + CRLF + split_value[index + 1] + CRLF
            result.append(deserialize_bytes(val))
            index += 2
        elif split_value[index][0] in [':', '+', '-']:
            val = split_value[index] + CRLF
            result.append(deserialize(val))
            index += 1
        elif split_value[index].startswith('*'):
            start = [r.start() for r in re.finditer(CRLF, value)][index] + 2
            array_result = deserialize_array(value[start:])
            index += 1
            for _ in range(len(array_result)):
                if split_value[index][0].startswith('$'):
                    index += 2
                elif split_value[index][0] in [':', '+', '-']:
                    index += 1
            result.append(array_result)
    return result


def serialize_null() -> str:
    return RedisType.BULK_STRING.value + '-1'


def deserialize_null() -> None:
    return None


def deserialize_error(value) -> str:
    return deserialize_string(value)


def serialize(value: str, serializer_type: RedisType) -> bytes:
    if serializer_type == RedisType.STRING:
        serialized_value = serialize_string(value)
    elif serializer_type == RedisType.BULK_STRING:
        serialized_value = serialize_bytes(value)
    elif serializer_type == RedisType.INTEGER:
        serialized_value = serialize_integer(value)
    elif serializer_type == RedisType.ARRAY:
        serialized_value = serialize_array(value)
    elif serializer_type == RedisType.ERROR:
        serialized_value = serialize_error(value)
    elif serializer_type == RedisType.NULL:
        serialized_value = serialize_null()
    else:
        raise Exception()
    return (serialized_value + CRLF).encode('utf-8')


def deserialize(value: str):
    if value == '$-1\r\n':
        return deserialize_null()
    v = value[0]
    if v == '+':
        return deserialize_string(value)
    if v == '-':
        return deserialize_error(value)
    if v == ':':
        return deserialize_integer(value)
    if v == '$':
        return deserialize_bytes(value)
    if v == '*':
        return deserialize_array(value)
    raise Exception()


def process_data(data: bytes) -> bytes:
    # try:
    data = data.decode('utf-8')
    data = deserialize(data)
    # except Exception as e:
    #     print(str(e))
    #     print(data)
    if data[0].lower() == 'ping':
        if len(data) == 1:
            message = serialize('PONG', RedisType.STRING)
        elif len(data) == 2:
            message = serialize(data[1], RedisType.BULK_STRING)
        else:
            message = serialize(argument_error.format('ping'), RedisType.ERROR)
    elif data[0].lower() == 'echo':
        if len(data) == 2:
            message = serialize(data[1], RedisType.BULK_STRING)
        else:
            message = serialize(argument_error.format('echo'), RedisType.ERROR)
    elif data[0].lower() == 'set':
        if len(data) < 2:
            return serialize(argument_error.format('set'), RedisType.ERROR)
        else:
            expire_time = -1
            message = serialize('OK', RedisType.STRING)
            idx = 3
            while idx < len(data):
                option = data[idx].lower()
                if option in ['ex', 'px', 'eaxt', 'pxat']:
                    if expire_time > 0 or idx == len(data) - 1:
                        return serialize(syntax_error, RedisType.ERROR)
                    data_expire_time = data[idx + 1]
                    if not data_expire_time.isdigit():
                        return serialize(type_error, RedisType.ERROR)
                    data_expire_time = int(data_expire_time)
                    if data_expire_time <= 0:
                        return serialize(expire_time_error.format('set'), RedisType.ERROR)
                    if option == 'ex' or option == 'px':
                        condition = {'seconds' if option == 'ex' else 'milliseconds': data_expire_time}
                        expire_time = int((datetime.datetime.now() + datetime.timedelta(**condition)).timestamp())
                    else:
                        try:
                            expire_time = data_expire_time / 1000 if option == 'pxat' else data_expire_time
                            if datetime.datetime.fromtimestamp(expire_time) < datetime.datetime.now():
                                return serialize(expire_time_error.format('set'), RedisType.ERROR)
                        except ValueError:
                            return serialize(syntax_error, RedisType.ERROR)
                    idx += 2
                else:
                    return serialize(syntax_error, RedisType.ERROR)
            stored_data[data[1]] = {'value': str(data[2]), 'expiration': expire_time}
    elif data[0].lower() == 'get':
        if len(data) != 2:
            message = serialize(argument_error.format('get'), RedisType.ERROR)
        else:
            if data[1] in stored_data:
                value = stored_data[data[1]]
                if value['expiration'] == -1 or int(datetime.datetime.now().timestamp()) <= value['expiration']:
                    if isinstance(stored_data[data[1]]['value'], LinkedList):
                        message = serialize(wrong_type_list_error, RedisType.ERROR)
                    else:
                        message = serialize(stored_data[data[1]]['value'], RedisType.BULK_STRING)
                else:
                    del stored_data[data[1]]
                    message = serialize('', RedisType.NULL)
            else:
                message = serialize('', RedisType.NULL)
    elif data[0].lower() == 'exists':
        if len(data) == 1:
            message = serialize(argument_error.format('exists'), RedisType.ERROR)
        else:
            counter = 0
            for key in data[1:]:
                value = stored_data.get(key)
                if value and (value['expiration'] == -1 or
                              int(datetime.datetime.now().timestamp()) <= value['expiration']):
                    counter += 1
            message = serialize(counter, RedisType.INTEGER)
    elif data[0].lower() == 'del':
        if len(data) == 1:
            message = serialize(argument_error.format('del'), RedisType.ERROR)
        else:
            counter = 0
            for key in data[1:]:
                value = stored_data.pop(key, None)
                if value and (value['expiration'] == -1 or
                              int(datetime.datetime.now().timestamp()) <= value['expiration']):
                    counter += 1
            message = serialize(counter, RedisType.INTEGER)
    elif data[0].lower() == 'incr' or data[0].lower() == 'decr':
        command = data[0].lower()
        if len(data) != 2:
            message = serialize(argument_error.format(command), RedisType.ERROR)
        else:
            race_lock.acquire()
            existing_value = stored_data.get(data[1], {})
            if existing_value and not existing_value['value'].isdigit():
                message = serialize(type_error, RedisType.ERROR)
            else:
                if command == 'incr':
                    new_value = int(existing_value.get('value', 0)) + 1
                else:
                    new_value = int(existing_value.get('value', 0)) - 1
                expire_time = existing_value.get('expiration', -1)
                stored_data[data[1]] = {'value': str(new_value), 'expiration': expire_time}
                message = serialize(new_value, RedisType.INTEGER)
            race_lock.release()
    elif data[0].lower() == 'llen':
        if len(data) != 2:
            message = serialize(argument_error.format('llen'), RedisType.ERROR)
        else:
            value = stored_data.get(data[1])
            value = value['value'] if value else []
            if isinstance(value, LinkedList):
                message = serialize(len(value), RedisType.INTEGER)
            else:
                message = serialize(wrong_type_list_error, RedisType.ERROR)
    elif data[0].lower() == 'lrange':
        if len(data) != 4:
            message = serialize(argument_error.format('lrange'), RedisType.ERROR)
        else:
            try:
                start, stop = int(data[2]), int(data[3])
            except (TypeError, ValueError):
                message = serialize(type_error, RedisType.ERROR)
            else:
                value = stored_data.get(data[1], {}).get('value', [])
                if isinstance(value, LinkedList):
                    message = serialize(value.traverse(start, stop), RedisType.ARRAY)
                else:
                    message = serialize(wrong_type_list_error, RedisType.ERROR)
    elif data[0].lower() == 'lpush' or data[0].lower() == 'rpush':
        command_name = data[0].lower()
        if len(data) < 3:
            message = serialize(argument_error.format(command_name), RedisType.ERROR)
        else:
            race_lock.acquire()
            if data[1] in stored_data:
                value = stored_data[data[1]]['value']
                if isinstance(value, LinkedList):
                    if command_name == 'lpush':
                        value.insert_first(*data[2:])
                    else:
                        value.insert_last(*data[2:])
                    message = serialize(len(value), RedisType.INTEGER)
                else:
                    message = serialize(wrong_type_list_error, RedisType.ERROR)
            else:
                value = LinkedList()
                if command_name == 'lpush':
                    value.insert_first(*data[2:])
                else:
                    value.insert_last(*data[2:])
                stored_data[data[1]] = {'value': value, 'expiration': -1}
                message = serialize(len(value), RedisType.INTEGER)
            race_lock.release()
    else:
        error_message = unknown_error.format(data[0], ', '.join(f'`{d}`' for d in data[1:]))
        message = serialize(error_message, RedisType.ERROR)
    return message
