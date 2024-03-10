from app.main import deserialize, serialize
from app.enums import RedisObject, RedisType

examples = [
    RedisObject("$-1\r\n", RedisType.NULL, None),
    RedisObject("*1\r\n$4\r\nping\r\n", RedisType.ARRAY, [b'ping']),
    RedisObject("*2\r\n$4\r\necho\r\n$11\r\nhello world\r\n", RedisType.ARRAY, [b'echo', b'hello world']),
    RedisObject("*2\r\n$3\r\nget\r\n$3\r\nkey\r\n", RedisType.ARRAY, [b'get', b'key']),
    RedisObject("+OK\r\n", RedisType.STRING, 'OK'),
    RedisObject("-Error message\r\n", RedisType.ERROR, 'Error message'),
    RedisObject("$0\r\n\r\n", RedisType.BULK_STRING, b''),
    RedisObject("+hello world\r\n", RedisType.STRING, 'hello world'),
    RedisObject("*0\r\n\r\n", RedisType.ARRAY, []),
]


def test_deserialize():
    for example in examples:
        assert deserialize(example.resp_value) == example.value
