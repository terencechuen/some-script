import Adafruit_DHT
import RPi.GPIO as gpio

from modules.UUGear import *

input_value_type = sys.argv[1]
input_gpio_id = sys.argv[2]


def get_dht11_value(value_type, value_id):
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, value_id)
    if humidity is not None and temperature is not None:
        if value_type == 'tem':
            output = temperature
        elif value_type == 'hum':
            output = humidity
        else:
            output = 'dht11 error'
    else:
        output = 'dht11 error'
    return str(output)


def get_flame_sensor_value(value_id):
    gpio.setmode(gpio.BCM)
    gpio.setup(int(value_id), gpio.IN)
    output = gpio.input(int(value_id))
    return str(output)


if input_value_type == 'tem':
    print(get_dht11_value('tem', input_gpio_id))
elif input_value_type == 'hum':
    print(get_dht11_value('hum', input_gpio_id))
elif input_value_type == 'flame':
    print(get_flame_sensor_value(input_gpio_id))
else:
    print('input error')
    sys.exit(0)
