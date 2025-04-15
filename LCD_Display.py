from machine import I2C, Pin
from i2c_lcd import I2cLcd
from time import sleep

# Initialize I2C: GP0 = SDA, GP1 = SCL
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

# Scan for I2C address
devices = i2c.scan()
if not devices:
    print("LCD not found!")
else:
    lcd = I2cLcd(i2c, devices[0], 2, 16)  # 2 lines, 16 columns
    lcd.clear()
    
    lcd.move_to(0, 0)  # first row
    lcd.putstr("Oulu")
    
    lcd.move_to(0, 1)  # second row
    lcd.putstr("Temp:42 Hum:60")
