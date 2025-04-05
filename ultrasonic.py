def ultra():
    # emitting the pulse
   trigger.low()
   utime.sleep_us(2)
   trigger.high()
   utime.sleep_us(5)
   trigger.low()

    # waiting for the sensor to start listening
   while echo.value() == 0:
        # listening starts
       signaloff = utime.ticks_us()

    # waiting for the sensor to receive the pulse
   while echo.value() == 1:
        # listening ends
       signalon = utime.ticks_us()

    # how long the pulse traveled back and forth
   timepassed = signalon - signaloff
   # distance from the object in cm
   distance = round((timepassed * 0.0343) / 2)
   return distance 
