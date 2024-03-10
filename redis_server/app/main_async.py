import argparse
import asyncio
import sys
from typing import Dict

from enums import RedisType
from serializers import deserialize, serialize

parser = argparse.ArgumentParser(description='arguments for redis server')
parser.add_argument('-p', help='custom port number', default=6604, type=int)
args = parser.parse_args()

HOST = '127.0.0.1'
PORT = int(args.p)
argument_error = 'wrong number of arguments for \'{}\' command'
unknown_error = 'ERR unknown command `{}`, with args beginning with: {}'

stored_data: Dict[str, str] = {}


async def handle_request(reader: asyncio.streams.StreamReader,
                         writer: asyncio.streams.StreamWriter) -> None:
    while True:
        try:
            data = await reader.read(1024)
            print(data)
            if not data:
                return

            data = data.decode('utf-8')
            data = deserialize(data)
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
                if len(data) != 3:
                    message = serialize(argument_error.format('set'), RedisType.ERROR)
                else:
                    stored_data[data[1]] = str(data[2])
                    message = serialize('OK', RedisType.STRING)
            elif data[0].lower() == 'get':
                if len(data) != 2:
                    message = serialize(argument_error.format('get'), RedisType.ERROR)
                else:
                    if data[1] in stored_data:
                        message = serialize(stored_data[data[1]], RedisType.BULK_STRING)
                    else:
                        message = serialize('', RedisType.NULL)
            else:
                error_message = unknown_error.format(data[0], ', '.join(f'`{d}`' for d in data[1:]))
                message = serialize(error_message, RedisType.ERROR)
            writer.write(message)
            await writer.drain()
        except (KeyboardInterrupt, UnicodeDecodeError):
            writer.close()
            return


async def run_server():
    try:
        server = await asyncio.start_server(handle_request, HOST, PORT)
        print(f'running redis server on {HOST}:{PORT}')
        async with server:
            await server.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    asyncio.run(run_server())
