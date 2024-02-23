from dataclasses import dataclass
from datetime import datetime, timedelta
from threading import Lock

lock_race = Lock()


def check_setting_args(func):
    def inner(*args, **kwargs):
        if not 6 < len(args) < 10:
            return 'ERROR'
        if not args[3].isdigit() or not args[5].isdigit():
            return 'ERROR'
        if not args[4].isdigit() and (not args[4][1:].isdigit() and args[4][0] != '-'):
            return 'ERROR'
        if args[0] == 'cas' and not (7 < len(args) < 10 or args[-2].isdigit()):
            return 'ERROR'
        return func(*args, **kwargs)
    return inner


def check_numeric_changes_args(func):
    def wrapper(*args, **kwargs):
        if len(args) != 4 or not args[-1].isdigit():
            return 'ERROR'
        return func(*args, **kwargs)
    return wrapper


@dataclass
class MemcacheEntity:
    cas_id: int
    flags: int
    value: str
    bytes: int
    expiration_time: int = 0


class Memcache:
    _STORED = {}
    _SIZE_LIMIT = 100000
    _META = {'LAST_CAS_ID': 0,
             'SIZE': 0,}

    @classmethod
    def set_expiration_time(cls, _seconds):
        _seconds = int(_seconds)
        if _seconds == 0:
            return _seconds

        if _seconds < 0:
            return -1

        return int((datetime.now() + timedelta(seconds=_seconds)).timestamp())

    def __set_value(self, *inputs):
        key = inputs[1]
        total_size = self._META['SIZE'] + int(inputs[4])
        if key in self._STORED:
            total_size -= int(self._STORED[key].bytes)
        if total_size > self._SIZE_LIMIT:
            return 'SIZE_LIMIT'

        self._STORED[key] = MemcacheEntity(
            cas_id=self._META['LAST_CAS_ID'] + 1,
            flags=inputs[2],
            expiration_time=Memcache.set_expiration_time(inputs[3]),
            bytes=inputs[4],
            value=inputs[-1],
        )
        self._META['LAST_CAS_ID'] += 1
        self._META['SIZE'] = total_size
        return 'STORED'

    @check_setting_args
    def set(self, *args, **kwargs):
        _cas_id = kwargs.get('cas_id', None)
        if _cas_id:
            if args[1] not in self._STORED:
                return 'NOT_FOUND'
            lock_race.acquire()
            if self._STORED[args[1]].cas_id == int(_cas_id):
                response = self.__set_value(*args)
            else:
                response = 'EXISTS'
            lock_race.release()
        else:
            response = self.__set_value(*args)

        no_reply = True if args[5] == '[noreply]' else False
        if no_reply:
            return ''
        return response

    @check_setting_args
    def add(self, *args, **kwargs):
        if args[1] not in self._STORED:
            return self.set(*args, **kwargs)
        return 'NOT_STORED'

    @check_setting_args
    def replace(self, *args, **kwargs):
        if args[1] in self._STORED:
            return self.set(*args, **kwargs)
        return 'NOT_STORED'

    @check_setting_args
    def append(self, *args, **kwargs):
        if args[1] in self._STORED:
            entity = self._STORED[args[1]]
            new_value = entity.value + args[-1]
            new_bytes_count = str(int(args[4]) + int(entity.bytes))
            args = args[:4] + (new_bytes_count,) + args[5:-1] + (new_value,)
            return self.set(*args, **kwargs)
        return 'NOT_STORED'

    @check_setting_args
    def prepend(self, *args, **kwargs):
        if args[1] in self._STORED:
            entity = self._STORED[args[1]]
            new_value = args[-1] + entity.value
            new_bytes_count = str(int(args[4]) + int(entity.bytes))
            args = args[:4] + (new_bytes_count,) + args[5:-1] + (new_value,)
            return self.set(*args, **kwargs)
        return 'NOT_STORED'

    @check_setting_args
    def cas(self, *args, **kwargs):
        return self.set(cas_id=args[-2], *args, **kwargs)

    def get(self, *args, **kwargs):
        key = args[1]
        if key in self._STORED:
            entity = self._STORED[key]
            expiration_time = entity.expiration_time
            if expiration_time == 0 or datetime.fromtimestamp(expiration_time) >= datetime.now():
                return f'VALUE {key} {entity.flags} {entity.bytes}\r\n{entity.value}\r\nEND'
            del self._STORED[key]
        return 'END'

    def gets(self, *args, **kwargs):
        key = args[1]
        if key in self._STORED:
            entity = self._STORED[key]
            expiration_time = entity.expiration_time
            if expiration_time == 0 or datetime.fromtimestamp(expiration_time) >= datetime.now():
                return f'VALUE {key} {entity.flags} {entity.bytes} {entity.cas_id}\r\n{entity.value}\r\nEND'
            del self._STORED[key]
        return 'END'

    def delete(self, *args, **kwargs):
        no_reply = len(args) == 3 and args[-1] == '[noreply]'
        if len(args) == 2 or no_reply:
            entity = self._STORED.pop(args[1], None)
            if entity:
                self._META['SIZE'] -= int(entity.bytes)
            result = 'NOT_FOUND' if entity is None else 'DELETED'
        else:
            result = 'ERROR'
        return '' if no_reply else result

    @check_numeric_changes_args
    def incr(self, *args, **kwargs):
        key = args[1]
        if key not in self._STORED:
            return 'NOT_FOUND'

        if not self._STORED[key].value.isdigit():
            return 'CLIENT_ERROR cannot increment non-numeric value'

        lock_race.acquire()
        entity = self._STORED[key]
        new_value = str(int(entity.value) + int(args[2]))
        new_bytes_count = len(new_value.encode()) - int(entity.bytes)
        entity.value = new_value
        entity.bytes = str(len(new_value.encode()))
        self._META['SIZE'] += new_bytes_count
        lock_race.release()
        return str(new_value)

    @check_numeric_changes_args
    def decr(self, *args, **kwargs):
        key = args[1]
        if key not in self._STORED:
            return 'NOT_FOUND'

        if not self._STORED[key].value.isdigit():
            return 'CLIENT_ERROR cannot decrement non-numeric value'

        lock_race.acquire()
        entity = self._STORED[key]
        new_value = str(int(entity.value) - int(args[2]))
        new_bytes_count = len(new_value.encode()) - int(entity.bytes)
        entity.value = new_value
        entity.bytes = str(len(new_value.encode()))
        self._META['SIZE'] += new_bytes_count
        lock_race.release()
        return str(new_value)

    def flush_all(self, *args, **kwargs):
        self._STORED.clear()
        self._META.update({'LAST_CAS_ID': 0, 'SIZE': 0})
        return 'OK'

    def error(self, *args, **kwargs):
        return 'ERROR'

    def dispatch(self, command, *args, **kwargs):
        handler = getattr(self, command, self.error)
        return handler(*args, **kwargs)

    def run_command(self, *args, **kwargs):
        command_name = args[0] if len(args) else 'error'
        return self.dispatch(command_name, *args, **kwargs)
