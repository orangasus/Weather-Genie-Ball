I2C_ADDR     = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

WIFI_SSID = 'orangasus_net_Guest'
WIFI_PASSWORD = 'NiceTry1'

NUM_LEDS = 60
MAX_TEMP = 50
MIN_TEMP = -50
STRIP_ACTIVE = False

# Ultrasonic sensor constants
DETECTION_DISTANCE = 20  # Detection threshold in centimeters
TIMEOUT = 250_000        # 250ms timeout

# API requests constants
OPERATION_TIMEOUT = 5	# seconds
MAX_REQUESTS = 3

DISPLAY_TEXT = "{0}\n{1} - {2}c {3}%"

WEATHER_API_KEY = ':)'
WEATHER_URL = "https://api.openweathermap.org/data/3.0/onecall?lat={0}&lon={1}&appid={2}"
LOC_BY_IP_API_KEY = ':)'
LOC_BY_IP_URL = "https://ipinfo.io/json?token={0}"

LOADING_COLOR = (0, 50, 0)
LED_BRIGHTNESS = 0.1
GLOWDOWN_SPEED = 0.003
GLOWUP_SPEED = 0.01
