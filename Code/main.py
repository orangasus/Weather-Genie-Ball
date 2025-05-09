import utime
import usocket
import machine
from machine import I2C, Pin
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
import network
import urequests
from constants import *
from neopixel import NeoPixel


# Gadget state parameters
CURRENT_IP = None
CURRENT_CITY = None
CURRENT_LAT = None
CURRENT_LON = None
WEATHER_DATA = None
CURRENT_COLOR = None

# Sensors/actuators objects
# Variables for the Ultrasonic sensor
trigger = machine.Pin(8, machine.Pin.OUT)
echo = machine.Pin(9, machine.Pin.IN)
# Variables for the LED Strip
led_strip = NeoPixel(Pin(5, Pin.OUT), NUM_LEDS)
# Variables for the LCD Display
i2c = I2C(0, sda=machine.Pin(12), scl=machine.Pin(13), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

# Network handling object
wlan = network.WLAN(network.STA_IF)
  
# Makes api request to get lat/long and city by IP address
def get_info_from_ip():
    requests_count = 0
    
    while requests_count < MAX_REQUESTS:     
        try:
            data_from_ip = urequests.get(LOC_BY_IP_URL.format(LOC_BY_IP_API_KEY), timeout=OPERATION_TIMEOUT).json()
            
            lat, lon = data_from_ip['loc'].split(',')
            city = data_from_ip['city']
            
            global CURRENT_CITY, CURRENT_LAT, CURRENT_LON
            CURRENT_CITY = city
            CURRENT_LAT = lat
            CURRENT_LON = lon
            return {'lat':lat, 'lon':lon, 'city':city}
        
        except Exception as e:
            print(f"--> Exception: {e}")
            requests_count += 1
            print("--> Timout, new sending new request...")
    
        utime.sleep(1)
        
    print("--> Max requests reached!")
    return -1
    

# Connects to WiFi
def connect_to_wifi():
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        pass
    global CURRENT_IP
    CURRENT_IP = (wlan.ifconfig())[0]
    utime.sleep(1)


# Makes LED Strip glow up, slowly increasing brightness
def led_strip_glowup(color):
    for i in range(0, 100):
        led_strip.fill((round(color[0] * i/100), round(color[1] * i/100), round(color[2] * i/100)))
        led_strip.write()
        utime.sleep(GLOWUP_SPEED)


# Makes LED Strip glow down, slowly decreasing brightness
def led_strip_glowdown(color):
    for i in range(100, -1, -1):
        led_strip.fill((round(color[0] * i/100), round(color[1] * i/100), round(color[2] * i/100)))
        led_strip.write()
        utime.sleep(GLOWDOWN_SPEED)


# Makes API request to fetch current weather params by lat/long
def get_weather_data_by_location():
    request_count = 0
    
    while request_count < MAX_REQUESTS:
        request_start = utime.ticks_ms()
        
        try: 
            url = WEATHER_URL.format(CURRENT_LAT, CURRENT_LON, WEATHER_API_KEY)
            weather_data = urequests.get(url, timeout=OPERATION_TIMEOUT).json()
            
            weather_state = weather_data['current']['weather'][0]['main']
            print(weather_state)
            weather_dict = {'temperature': round(weather_data['current']['temp'] - 272), 'humidity':weather_data['current']['humidity'],
                            'weather_state':weather_state}  
            
            global WEATHER_DATA
            WEATHER_DATA = weather_dict
            return 0
        
        except Exception as e:
            print(f"--> Exception: {e}")
            request_count += 1
            print("--> Timout, new sending new request...")
        
        utime.sleep(1)
            
    print("--> Max requests reached!")
    return -1
    

# Displays weather stats on the LCD display
def display_weather_data():
    lcd.backlight_on()
    lcd.clear()
    lcd.putstr(DISPLAY_TEXT.format(CURRENT_CITY, WEATHER_DATA['weather_state'], WEATHER_DATA['temperature'], WEATHER_DATA['humidity']))
    

# Turns on the LED Strip
def led_strip_on():
    color = calculate_rgb_for_temp(WEATHER_DATA['temperature'])
    global CURRENT_COLOR
    CURRENT_COLOR = color
    print(f"--> Turning on the LED, color: {color}")
    led_strip_glowup(color)
    

# Turns off the LED Strip
def led_strip_off():
    print(f"--> Shutting off the LED")
    global CURRENT_COLOR
    led_strip_glowdown(CURRENT_COLOR)
    CURRENT_COLOR = None
    

# Calculates RGB parameter for LED Strip based on current temperature
def calculate_rgb_for_temp(temp):
    if temp > MAX_TEMP:
        temp = MAX_TEMP
    elif temp < MIN_TEMP:
        temp = MIN_TEMP
        
    norm_temp = (temp - MIN_TEMP)/(MAX_TEMP-MIN_TEMP)
    red = round(LED_BRIGHTNESS * 255 * norm_temp**1.5)
    green = round(LED_BRIGHTNESS * 255 * 2 * (norm_temp - norm_temp**2))
    blue = round(LED_BRIGHTNESS * 255 * (1 - norm_temp**1.5))
    return (red,green,blue)


# Measures current distance to the object in front of the ultrasonic sensor
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


# Checks if object in front of the ultrasonic sensor is within detection range
def interpret_distance():
    current_distance = measure_distance()
    if current_distance < DETECTION_DISTANCE:
        return True
    return False


# Turns on the ball by calling all necessary functions after detecting object within range
def activate_ball():
    led_strip_glowup(LOADING_COLOR)
    lcd.display_on()
    lcd.backlight_on()
    
    if weather_function() == 0:  
        lcd.clear()
        led_strip_on()
        display_weather_data()
        global STRIP_ACTIVE
        STRIP_ACTIVE = True
    

# Turns off the ball, if detects object withing range and ball currently active, by calling all necessary functions
def deactivate_ball():
    lcd.clear()
    led_strip_off()
    lcd.backlight_off()
    lcd.display_off()
    global STRIP_ACTIVE
    STRIP_ACTIVE = False
   

# Conducts initial setup once the ball is connected to power source
def setup():
    global STRIP_ACTIVE
    STRIP_ACTIVE = False
    
#     led_strip_off()
    lcd.clear()
    
    lcd.putstr("Connecting\nTo WiFi...")
    connect_to_wifi()
    print(f"--> WiFi Connected; IP: {CURRENT_IP}")
    lcd.clear()
    
    lcd.putstr("Fetching\nLocation...")
    data_from_ip = get_info_from_ip()
    if data_from_ip == -1:
        print("--> Failed to fetch IP data :(")
        lcd.clear()
        lcd.putstr("Fetch IP: Failed\nRestart Gadget")
        return -1
    else:
        print(f"--> IP data fetched: {data_from_ip}")
        lcd.clear()
        lcd.putstr("Setup Complete!")
        led_strip_glowup(LOADING_COLOR)
        return 0


# Controls weather-related logic e.g. fetching weather, displaying it, making necessary checks
def weather_function():
    lcd.clear()
    lcd.putstr("Fetching\nWeather...")
    led_strip_glowdown(LOADING_COLOR)
    if get_weather_data_by_location() == -1:
        print("--> Failed to Weather data :(")
        lcd.clear()
        lcd.putstr("Weather: Failed\nRestart Gadget")
        return -1
    else:
        lcd.clear()
        lcd.putstr("All Done!")
        print(f"--> Weather data fetched: {WEATHER_DATA}")
        return 0


# Main loop function
def main():
    global STRIP_ACTIVE
    
    if setup() == 0:
        while True:
            gesture_detected = interpret_distance()
            if gesture_detected and not STRIP_ACTIVE:
                activate_ball()
                utime.sleep(1)
                
            elif gesture_detected and STRIP_ACTIVE:
                deactivate_ball()
                utime.sleep(1)
            utime.sleep(0.1)
    
    
if __name__ == "__main__":  
    main()
