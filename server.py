#-*- coding: UTF-8 -*-

import asyncio
import os
import requests
import sys
import websockets
import logging

from scale.reader_stub import Scale
from time import sleep
from config import config

env = os.getenv('PYTHON_ENV', 'production')

# DYMO M5
VENDOR_ID = 0x0922
PRODUCT_ID = 0x8005

empty = True
times_full = 0


# create logger
logging.basicConfig(filename='/var/log/coffeescale.log',level=logging.DEBUG)
logger = logging.getLogger('server')

def producer():
    global empty
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
    global empty, times_full

    logger.info("Listening to weight. Empty:{0}".format(empty))

    while True:
        result = producer()
        logger.info("Got result: {0} and empty is {1}".format(result[0], empty))
        if (result[0] != empty):
            if (result[0] == False):
                times_full = times_full + 1
                if (times_full >= 3):
                    __set_empty_and_post(hook, result)
            else:
                times_full = 0
                __set_empty_and_post(hook, result)

        yield from asyncio.sleep(3.0)

def __set_empty_and_post(hook, result):
    global empty
    empty = result[0]
    logger.info("Empty changed to {0}".format(empty))
    requests.post(hook, json = {'text':result[1]})

if __name__ == "__main__":
    argv = sys.argv
    num_args = len(argv)

    hook = argv[1]

    asyncio.get_event_loop().run_until_complete(weight_listener(hook))
    asyncio.get_event_loop().run_forever()
