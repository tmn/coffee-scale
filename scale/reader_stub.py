import random
import logging

__max = 300
__acc = 0

logger = logging.getLogger('reader_stub')

class Scale:
    def __init__(self, arg, meh):
        super(Scale, self).__init__()
        self.arg = arg

    def read(self):
        global __acc
        __acc = 0
        __max = 10

        __acc = __acc + random.randint(1, __max)
        if __acc < __max:
            return __acc

        __acc = 0
        return __max

    def is_empty(self):
        return self.read() <= 5

    def has_new_coffee(self):
        return self.read() > 5
