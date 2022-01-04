import time
import ssl
import wifi
import socketpool
import adafruit_requests
import board
import neopixel
import digitalio
import touchio

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
np[0] = (255, 0, 0)
time.sleep(2)
np[0] = (0, 0, 0)

touch_A2 = touchio.TouchIn(board.A2)  # on
touch_TX = touchio.TouchIn(board.TX)  # off

touch_sensors = [touch_TX, touch_A2]

for sensor in touch_sensors:
    sensor.threshold = 30000

HUE_URL = 'http://' + secrets["ip_address"] + \
    '/api/' + secrets["api_id"] + '/groups/12/action'

print("Connecting to %s" % secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s!" % secrets["ssid"])
print("My IP address is", wifi.radio.ipv4_address)

np[0] = (0, 255, 0)
time.sleep(2)
np[0] = (0, 0, 0)

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
            np[0] = (50, 50, 50)
            time.sleep(2)
            np[0] = (0, 0, 0)
            data = '{{"scene":"{}"}}'.format(secrets["on_scene"])
            new_state = "on"
        if touch_TX.value:  # off
            print("TX touched!")
            np[0] = (90, 0, 127)
            time.sleep(2)
            np[0] = (0, 0, 0)
            data = '{"on":false}'
            new_state = "off"

        if current_state != new_state:
            is_touched = False
            current_state = new_state
            print("PUTing data to {0}".format(HUE_URL))
            response = requests.put(HUE_URL, data=data)
            print("-" * 40)
            print(response.status_code)
            print("-" * 40)
            response.close()
