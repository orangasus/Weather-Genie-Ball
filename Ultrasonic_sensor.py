import machine
import utime

# Pin configuration (adjust according to your wiring)
trigger = machine.Pin(15, machine.Pin.OUT)
echo = machine.Pin(14, machine.Pin.IN)
DETECTION_DISTANCE = 20  # Detection threshold in centimeters
TIMEOUT = 250_000        # 250ms timeout (~4m max range)

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

# Initialization delay (critical for Wokwi)
utime.sleep(1)

# Main loop
while True:
    current_distance = measure_distance()
    
    if current_distance == -1:
        print("⚠️ Measurement error: No echo detected")
    elif current_distance < DETECTION_DISTANCE:
        print(f"🚨 Object detected! Distance: {current_distance} cm")
    else:
        print(f"📏 Distance: {current_distance} cm")
    
    utime.sleep(0.1)  # Measurement interval
