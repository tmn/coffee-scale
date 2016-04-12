import usb.core
import usb.util

VENDOR_ID = 0x0922
PRODUCT_ID = 0x8005

device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)

for cfg in device:
  for intf in cfg: 
    if device.is_kernel_driver_active(intf.bInterfaceNumber):
      try:
        device.detach_kernel_driver(intf.bInterfaceNumber)
      except usb.core.USBError as e:
        sys.exit("Could not detach kerner driver from interface({0}): {1}".format(intf.bInterfaceNumber, str(e)))

device.set_configuration()

endpoint = device[0][(0,0)][0]

attempts = 10
data = None

while data is None and attempts > 0:
    try:
        data = device.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize)

    except usb.core.USBError as e:
        data = None
        if e.args == ('Operation timed out',):
            attempts -= 1
            continue
        else:
            print('ERROR {}'.format(e.args))
            attempts -= 1
            continue

print(data)
