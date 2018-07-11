from UUGear import *
import sys

input_gpio_id = sys.argv[1]

UUGearDevice.setShowLogs(0)
device = UUGearDevice('UUGear-Arduino-4608-5541')

if device.isValid():
    print ((float(device.analogRead(int(input_gpio_id))) * 5.0 / 1024.0) / (7500.0 / (30000.0 + 7500.0)))
    device.detach()
    device.stopDaemon()
else:
    print 'UUGear device is not correctly initialized.'