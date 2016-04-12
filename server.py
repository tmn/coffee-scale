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
print(env)

# DYMO M5
VENDOR_ID = 0x0922
PRODUCT_ID = 0x8005

empty = True

def producer():
    scale = Scale(VENDOR_ID, PRODUCT_ID)
    message = None
    if scale.is_empty() and not empty:
        return (True,'Tomt for :coffee: :disappointed:')
    elif scale.has_new_coffee() and empty:
        return (False,'Ny :coffee: !!')
    else:
        return (empty, "")

@asyncio.coroutine
def weight_listener(hook):
    global empty

    print("Listening to weight")

    while True:
        result = producer()

        if (result[0] != empty):
            empty = result[0]
            requests.post(hook, json = {'text':result[1]})

        yield from asyncio.sleep(1.0)


if __name__ == "__main__":
    argv = sys.argv
    num_args = len(argv)

    hook = argv[1]

    asyncio.get_event_loop().run_until_complete(weight_listener(hook))
    asyncio.get_event_loop().run_forever()
