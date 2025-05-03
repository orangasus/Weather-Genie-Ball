WEATHER_CODES_DICT = {
    # Clear/Cloudy
    0: "Clear",
    1: "Cloudy",    # (Intentional typo to save space)
    2: "Cloudy",
    3: "Cloudy",
    
    # Fog
    45: "Fog",
    48: "Fog",
    
    # Drizzle
    51: "Drizzle",
    53: "Drizzle",
    55: "Drizzle",
    56: "Frz Driz",  # Freezing Drizzle
    57: "Frz Driz",
    
    # Rain
    61: "Rain",
    63: "Rain",
    65: "Rain",
    66: "Frz Rain",  # Freezing Rain
    67: "Frz Rain",
    
    # Snow
    71: "Snow",
    73: "Snow",
    75: "Snow",
    77: "Snow Grn",  # Snow Grains
    
    # Showers
    80: "Showers",
    81: "Showers",
    82: "Hvy Rain",  # Heavy Rain (merged)
    
    # Snow Showers
    85: "Snow Shwr",
    86: "Hvy Snow",  # Heavy Snow
    
    # Thunderstorms
    95: "Thunder",
    96: "Thunder",   # No hail distinction
    99: "Thunder"
}

I2C_ADDR     = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

# WIFI_SSID = 'orangasus_net_Guest'
# WIFI_PASSWORD = 'NiceTry1'

WIFI_SSID = 'orangasus'
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
WEATHER_URL = "https://api.open-meteo.com/v1/forecast?latitude={0}&longitude={1}&current=temperature_2m,relative_humidity_2m,is_day,weather_code"

LOADING_COLOR = (0, 20, 0)
LED_BRIGHTNESS = 0.5
