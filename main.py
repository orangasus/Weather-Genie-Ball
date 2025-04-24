import utime
import machine
from machine import I2C, Pin
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
import network
import urequests
from constants import *
from neopixel import NeoPixel

I2C_ADDR     = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

WIFI_SSID = 'orangasus_net_Guest'
WIFI_PASSWORD = 'NiceTry1'

NUM_LEDS = 60
MAX_TEMP = 50
MIN_TEMP = -50
STRIP_ACTIVE = False

DETECTION_DISTANCE = 20  # Detection threshold in centimeters
TIMEOUT = 250_000        # 250ms timeout

CURRENT_IP = None
CURRENT_CITY = None
CURRENT_LAT = None
CURRENT_LON = None
WEATHER_DATA = None

onboard_led = machine.Pin("LED", Pin.OUT)
trigger = machine.Pin(8, machine.Pin.OUT)
echo = machine.Pin(9, machine.Pin.IN)
led_strip = NeoPixel(Pin(5, Pin.OUT), NUM_LEDS)
wlan = network.WLAN(network.STA_IF)
i2c = I2C(0, sda=machine.Pin(12), scl=machine.Pin(13), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)
    
# makes api request to get lat/long and city by ip address
def get_info_from_ip():
    data_from_ip = urequests.get("http://ip-api.com/json/").json()
    lat, lon = data_from_ip['lat'], data_from_ip['lon']
    city = data_from_ip['city']
    global CURRENT_CITY, CURRENT_LAT, CURRENT_LON
    CURRENT_CITY = city
    CURRENT_LAT = lat
    CURRENT_LON = lon
    return {'lat':lat, 'lon':lon, 'city':city}

# connects to wifi
def connect_to_wifi():
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        pass
    global CURRENT_IP
    CURRENT_IP = (wlan.ifconfig())[0]
    
def get_weather_data_by_location():
    weather_data = urequests.get(f"https://api.open-meteo.com/v1/forecast?latitude={CURRENT_LAT}&longitude={CURRENT_LON}&current=temperature_2m,relative_humidity_2m,is_day,weather_code").json()
    weather_code = weather_data['current']['weather_code']
    weather_state = WEATHER_CODES_DICT[weather_code]
    weather_dict = {'temperature': round(weather_data['current']['temperature_2m']), 'humidity':weather_data['current']['relative_humidity_2m'], 'weather_state':weather_state}  
    global WEATHER_DATA
    WEATHER_DATA = weather_dict
    
def display_weather_data():
    lcd.clear()
    lcd.putstr(f"{CURRENT_CITY}\n{WEATHER_DATA['weather_state']} - {WEATHER_DATA['temperature']}c {WEATHER_DATA['humidity']}%")
    
def led_strip_on():
    color = calculate_rgb_for_temp(WEATHER_DATA['temperature'])
    print(color)
    led_strip.fill(color)
    led_strip.write()
    
def led_strip_off():
    led_strip.fill((0,0,0))
    led_strip.write()
    
def calculate_rgb_for_temp(temp):
    if temp > MAX_TEMP:
        temp = MAX_TEMP
    elif temp < MIN_TEMP:
        temp = MIN_TEMP
    norm_temp = (temp - MIN_TEMP)/(MAX_TEMP-MIN_TEMP)
    red = round(255 * norm_temp**1.5)
    green = round(255 * 2 * (norm_temp - norm_temp**2))
    blue = round(255 * (1 - norm_temp**1.5))
    return (red,green,blue)

def measure_distance():
    # Send ultrasonic pulse
    trigger.low()
    utime.sleep_us(2)
    trigger.high()
    utime.sleep_us(5)
    trigger.low()

    # Wait for echo pulse start
    start_time = utime.ticks_us()
    while echo.value() == 0:
        if utime.ticks_diff(utime.ticks_us(), start_time) > TIMEOUT:
            return -1  # Timeout error
    pulse_start = utime.ticks_us()

    # Wait for echo pulse end
    start_time = utime.ticks_us()
    while echo.value() == 1:
        if utime.ticks_diff(utime.ticks_us(), start_time) > TIMEOUT:
            return -1  # Timeout error
    pulse_end = utime.ticks_us()

    # Calculate distance in cm
    pulse_duration = utime.ticks_diff(pulse_end, pulse_start)
    distance = (pulse_duration * 0.0343) / 2  # Speed of sound = 343m/s
    return round(distance)

def interpret_distance():
    current_distance = measure_distance()
    if current_distance < DETECTION_DISTANCE:
        return True
    return False
    
def main():
    global STRIP_ACTIVE
    led_strip_off()
    lcd.display_off()
    lcd.backlight_off()
    connect_to_wifi()
    print(f"--> WiFi Connected; IP: {CURRENT_IP}")
    data_from_ip = get_info_from_ip()
    print(f"--> IP data fetched: {data_from_ip}")
    get_weather_data_by_location()
    print(f"--> Weather data fetched: {WEATHER_DATA}")
    while True:
        gesture_detected = interpret_distance()
        if gesture_detected and not STRIP_ACTIVE:
            led_strip_on()
            lcd.display_on()
            lcd.backlight_on()
            display_weather_data()
            STRIP_ACTIVE = True
            utime.sleep(2)
        elif gesture_detected and STRIP_ACTIVE:
            led_strip_off()
            lcd.backlight_off()
            lcd.display_off()
            STRIP_ACTIVE = False
            utime.sleep(2)
        utime.sleep(0.1)
    
main()
