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


async def send_message(streams):
    print("Waiting for input")
    stdin, _ = await aioconsole.get_standard_streams()
    data = await stdin.read(100)
    for port, stream in streams.items():
        reader, writer = stream
        try:
            await ping(port, reader, writer)
        except ConnectionError:
            try:
                reader, writer = await asyncio.open_connection('127.0.0.1',
                                                               port)
                streams[port] = (reader, writer)
            except ConnectionRefusedError:
                # server is still down, let main loop reconnect
                pass
        finally:
            writer.write(data)


async def listen(port):
    server = await asyncio.start_server(receive_message, '127.0.0.1', port)
    async with server:
        await server.serve_forever()


async def ping(port, reader, writer):
    if reader.at_eof():
        raise ConnectionError
    try:
        await asyncio.wait_for(reader.readline(), timeout=0.1)
    except asyncio.TimeoutError:
        pass


async def connect(ports):
    streams = {}
    while True:
        for port in ports:
            # no registered connection to this server, make initial connection
            if not streams.get(port):
                try:
                    streams[port] = await asyncio.open_connection('127.0.0.1',
                                                                  port)
                except ConnectionRefusedError:
                    await asyncio.sleep(1)
        if len(streams) > 0:
            await send_message(streams)


async def main():
    on = sys.argv[1]
    peers = sys.argv[2].split(',')
    await asyncio.gather(listen(on), connect(peers))


if __name__ == '__main__':
    asyncio.run(main())
