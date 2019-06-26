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


async def send_message(writers):
    print("Waiting for input")
    stdin, _ = await aioconsole.get_standard_streams()
    while True:
        data = await stdin.read(100)
        if not data:
            break
        for writer in writers:
            writer.write(data)


async def listen(port):
    server = await asyncio.start_server(receive_message, '127.0.0.1', port)
    async with server:
        await server.serve_forever()


async def connect(ports):
    writers = []
    while len(writers) < len(ports):
        for port in ports:
            try:
                _, writer = await asyncio.open_connection('127.0.0.1', port)
                writers.append(writer)
            except ConnectionRefusedError:
                await asyncio.sleep(1)
    await send_message(writers)


async def main():
    on = sys.argv[1]
    peers = sys.argv[2].split(',')
    await asyncio.gather(listen(on), connect(peers))


if __name__ == '__main__':
    asyncio.run(main())
