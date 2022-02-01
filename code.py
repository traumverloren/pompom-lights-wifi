import time
import ssl
import wifi
import socketpool
import adafruit_requests
import board
import neopixel
import digitalio
import touchio
# import ipaddress

OFF = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (50, 50, 50)
GREEN = (0, 255, 0)
PURPLE = (90, 0, 127)

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# Remove these two lines on boards without board.NEOPIXEL_POWER.
np_power = digitalio.DigitalInOut(board.NEOPIXEL_POWER)
np_power.switch_to_output(value=False)
np = neopixel.NeoPixel(board.NEOPIXEL, 1)
np_power.value = True
np[0] = RED
time.sleep(2)
np[0] = OFF

touch_A2 = touchio.TouchIn(board.A2)  # on
touch_TX = touchio.TouchIn(board.TX)  # off

touch_sensors = [touch_TX, touch_A2]

for sensor in touch_sensors:
    sensor.threshold = 27000

HUE_URL = 'http://' + secrets["ip_address"] + \
    '/api/' + secrets["api_id"] + '/groups/12/action'

print("Connecting to %s" % secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s!" % secrets["ssid"])
print("My IP address is", wifi.radio.ipv4_address)

np[0] = GREEN
time.sleep(2)
np[0] = OFF

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

is_touched = False
data = ''
current_state = ''
new_state = ''

while True:

    if touch_TX.value or touch_A2.value:
        is_touched = True
        time.sleep(1)

    if is_touched:
        if touch_A2.value:  # on
            print("A2 touched!")
            data = '{{"scene":"{}"}}'.format(secrets["on_scene"])
            new_state = "on"
        if touch_TX.value:  # off
            print("TX touched!")
            data = '{"on":false}'
            new_state = "off"

        np[0] = WHITE if new_state == "on" else PURPLE
        print(data)
        print("PUTing data to {0}".format(HUE_URL))
        response = requests.put(HUE_URL, data=data)
        response.close()
        is_touched = False
        current_state = new_state
        time.sleep(2)
        np[0] = OFF

    # else:
    #     test_ping = wifi.radio.ping(
    #         ipaddress.ip_address(secrets["ip_address"]))
    #     print(test_ping)

    #     if test_ping == 0:
    #         wifi.radio.connect(secrets["ssid"], secrets["password"])
    #         print("Reconnected to %s!" % secrets["ssid"])
    #     time.sleep(0.5)
