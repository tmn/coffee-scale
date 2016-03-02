#-*- coding: UTF-8 -*-

import asyncio
import os
import requests
import sys
import websockets

from scale.reader import Scale
from time import sleep
from config import config

env = os.getenv('PYTHON_ENV', 'production')

# DYMO M5
VENDOR_ID = 0x0922
PRODUCT_ID = 0x8005

connected = set()
empty = True

@asyncio.coroutine
def producer():
    global empty
    scale = Scale(VENDOR_ID, PRODUCT_ID)
    message = None

    while True:
        if scale.is_empty() and not empty:
            empty = True
            return 'Tomt for :coffee: :disappointed:'
        elif scale.has_new_coffee() and empty:
            empty = False
            return 'Ny :coffee: !!'

        yield from asyncio.sleep(0.1)


@asyncio.coroutine
def consumer(message):
    global connected

    ## Listen to incomming stuff
    ## Handle incomming messages here
    print('CONSUMER {}'.format(message))


@asyncio.coroutine
def weight_listener(websocket, path):
    global connected

    connected.add(websocket)

    while True:
        listener_task = asyncio.async(websocket.recv())
        producer_task = asyncio.async(producer())
        done, pending = yield from asyncio.wait(
            [listener_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED)

        if listener_task in done:
            message = listener_task.result()
            yield from consumer(message)
        else:
            listener_task.cancel()

        if producer_task in done:
            message = producer_task.result()
            for ws in connected.copy():
                requests.post(utils.WEBHOOK, json={'text': message})
                try:
                    yield from ws.send(message)
                except:
                    connected.remove(ws)
        else:
            producer_task.cancel()

        yield from asyncio.sleep(0.1)

if __name__ == "__main__":
    argv = sys.argv
    num_args = len(argv)

    server = 'localhost' if num_args < 2 else argv[1]
    port = (int) (3000 if num_args < 3 else argv[2])

    start_server = websockets.serve(weight_listener, server, port)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
