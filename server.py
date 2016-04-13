#-*- coding: UTF-8 -*-

import asyncio
import os
import requests
import sys
import websockets
import logging
from threading import Thread

from scale.reader_stub import Scale
from api.api import ApiRequestHandler
from time import sleep
from config import config
from http.server import HTTPServer

env = os.getenv('PYTHON_ENV', 'production')

# DYMO M5
VENDOR_ID = 0x0922
PRODUCT_ID = 0x8005


times_full = 0
times_empty = 0
scale = Scale(VENDOR_ID, PRODUCT_ID)
empty = scale.is_empty()

# create logger
logging.basicConfig(filename='/var/log/coffeescale.log',level=logging.DEBUG,
                    format='%(asctime)s %(message)s')
logger = logging.getLogger('server')

def producer():
    global empty, scale
    message = None
    if scale.is_empty() and not empty:
        return (True,'Tomt for :coffee: :disappointed:')
    elif scale.has_new_coffee() and empty:
        return (False,'Ny :coffee: !!')
    else:
        return (empty, "")

@asyncio.coroutine
def weight_listener(hook):
    global empty, times_full, times_empty

    logger.info("Listening to weight. Empty:{0}".format(empty))

    while True:
        result = producer()
        logger.info("Got result: {0} and empty is {1}".format(result[0], empty))
        if (result[0] != empty):
            if (result[0] == False):
                times_full = times_full + 1
                times_empty = 0
                if (times_full >= 3):
                    __set_empty_and_post(hook, result)
            else:
                times_full = 0
                times_empty = times_empty + 1
                if (times_empty >= 3):
                    __set_empty_and_post(hook, result)

        yield from asyncio.sleep(3.0)

def __set_empty_and_post(hook, result):
    global empty
    empty = result[0]
    logger.info("Empty changed to {0}".format(empty))
    requests.post(hook, json = {'text':result[1]})

def run():
  logger.info('starting server...')

  # Server settings
  # Choose port 8080, for port 80, which is normally used for a http server, you need root access
  server_address = ('', 8080)
  handler = ApiRequestHandler
  handler.scale = scale
  httpd = HTTPServer(server_address, handler)
  logger.info('running server...')
  httpd.serve_forever()

if __name__ == "__main__":
    # Start API Server
    thread = Thread(target = run)
    thread.start()

    # Setup Slack webhook check loop
    argv = sys.argv
    hook = argv[1]
    asyncio.get_event_loop().run_until_complete(weight_listener(hook))
    asyncio.get_event_loop().run_forever()

    thread.join()
