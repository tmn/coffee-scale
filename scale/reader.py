import os, time
import usb.core
import usb.util
import logging
from sys import exit

logger = logging.getLogger('reader')

class Scale:
    weight_empty_value = None
    weight_new_coffee_value = None
    id_vendor = None
    id_product = None
    device = None

    def __init__(self, id_vendor, id_product, weight_empty_value=1900, weight_new_coffee_value=3000):
        self.id_vendor = id_vendor
        self.id_product = id_product
        self.weight_empty_value = weight_empty_value
        self.weight_new_coffee_value = weight_new_coffee_value

        self.device = self.__connect()

    def __read(self):
        if self.device is not None:
            data = self.__analyzeData(self.__grabData())
            self.__disconnect()
            return data

    def is_empty(self):
        if self.__read() <= self.weight_empty_value:
            return True

        return False

    def has_new_coffee(self):
        if self.__read() >= self.weight_new_coffee_value:
            return True

        return False

    def __connect(self):
        # find the USB device
        self.device = usb.core.find(idVendor=self.id_vendor, idProduct=self.id_product)

        if self.device is None:
            return self.device
        else:
            interface = 0

            if self.device.is_kernel_driver_active(interface) is True:
                self.device.detach_kernel_driver(interface)
                self.device.set_configuration()
                usb.util.claim_interface(self.device, interface)

        return self.device

    def __disconnect(self):
        interface = 0
        usb.util.release_interface(self.device, interface)

    def __analyzeData(self, data):
        DATA_MODE_GRAMS = 2
        DATA_MODE_OUNCES = 11
        grams = 0

        logger.debug("Got the following data {0}".format(data))

        if data != None:
            raw_weight = data[4] + data[5] * 256

        if raw_weight > 0:
            if data[2] == DATA_MODE_OUNCES:
                ounces = raw_weight * 0.1
                grams = round(ounces * 28.3495, 2)
            elif data[2] == DATA_MODE_GRAMS:
                grams = raw_weight

            logger.debug("Returned the following grams: {0}".format(grams))
            return grams

        logger.debug("Returned 0 grams")
        return 0


    def __grabData(self):
        # first endpoint
        endpoint = self.device[0][(0,0)][0]

        # read a data packet
        attempts = 10
        data = None

        while data is None and attempts > 0:
            try:
                data = self.device.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize)
            except usb.core.USBError as e:
                logger.warning("Got exception from weight. {0}".format(e))
                data = None
                if e.args == ('Operation timed out',):
                    attempts -= 1
                    continue

        return data
