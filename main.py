from machine import Pin
import neopixel
import time


def strip_off():
    led_strip.fill((0, 0, 0)) 
    led_strip.write()

def strip_on():       
    time.sleep(0.05)          
    led_strip.fill((10,0,0))  
    led_strip.write()
    

TURNED_ON = False
DEBOUNCE_MS = 200

last_press_time = 0


onboard_led = Pin("LED", Pin.OUT)
onboard_led.value(TURNED_ON)

power_slide = Pin(15, Pin.IN, Pin.PULL_UP)

# LED Strip Configuration
NUM_LEDS = 60  # Adjust this to match your strip length (e.g., 60 for 1m WS2812B)
led_strip = neopixel.NeoPixel(Pin(16), NUM_LEDS)

while True:
    if power_slide.value() == True and TURNED_ON == False:
        TURNED_ON = True
        onboard_led.high()
        strip_on()
    elif power_slide.value() == False and TURNED_ON == True:
        TURNED_ON = False
        onboard_led.low()
        strip_off()
    print(TURNED_ON)
    time.sleep(0.01)
    
        
