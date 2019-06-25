#!/usr/bin/env python3

import asyncio
import sys

import aioconsole


async def receive_message(reader, writer):
    print("Waiting for message")
    while True:
        data = await reader.read(100)
        if not data:
            break
        print(data.decode('utf-8'))


async def send_message(reader, writer):
    print("Waiting for input")
    stdin, _ = await aioconsole.get_standard_streams()
    while True:
        data = await stdin.read(100)
        if not data:
            break
        writer.write(data)


async def listen(port):
    server = await asyncio.start_server(receive_message, '127.0.0.1', port)
    async with server:
        await server.serve_forever()


async def connect(port):
    reader, writer = (None, None)
    while (reader, writer) == (None, None):
        try:
            reader, writer = await asyncio.open_connection('127.0.0.1', port)
            await send_message(reader, writer)
        except ConnectionRefusedError:
            await asyncio.sleep(1)


async def main():
    on = sys.argv[1]
    to = sys.argv[2]
    await asyncio.gather(listen(on), connect(to))


if __name__ == '__main__':
    asyncio.run(main())
