#!/usr/bin/env python3
#-*- coding: UTF-8 -*-

import asyncio
import os
import requests
import sys
import websockets

from scale.reader import Scale
from time import sleep

env = os.getenv('PYTHON_ENV', 'production')

# DYMO M5
VENDOR_ID = 0x0922
PRODUCT_ID = 0x8005

WEBHOOK = 'https://hooks.slack.com/services/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'

@asyncio.coroutine
def weight_listener(websocket, path):
    scale = Scale(VENDOR_ID, PRODUCT_ID)
    empty = True

    while True:
        grams = scale.read()
        message = ''

        if scale.is_empty() and not empty:
            empty = True
            msg = 'Tomt for :coffee: :disappointed:'
            #requests.post(WEBHOOK, json={'text': msg})
            yield from websocket.send(msg)

        elif scale.has_new_coffee() and empty:
            empty = False
            msg = 'Ny :coffee: !!'
            #requests.post(WEBHOOK, json={'text': msg})
            yield from websocket.send(msg)

        else:
            ## meh logic blah wuuop
            pass

        yield from asyncio.sleep(0.1)

if __name__ == "__main__":
    argv = sys.argv
    num_args = len(argv)

    server = 'localhost' if num_args < 2 else argv[1]
    port = (int) (3000 if num_args < 3 else argv[2])

    start_server = websockets.serve(weight_listener, server, port)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

    server()
