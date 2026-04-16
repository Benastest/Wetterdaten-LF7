from machine import I2C, Pin
import config
from lib.ssd1306 import SSD1306_I2C

def init_display():
    i2c = I2C(0, scl=Pin(config.I2C_SCL), sda=Pin(config.I2C_SDA))
    oled = SSD1306_I2C(config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT, i2c)
    oled.fill(0)
    oled.show()
    return oled

def draw_text(oled, text):
    oled.fill(0)
    y = 0
    for line in text.split("\n"):
        oled.text(line, 0, y)
        y += 10
    oled.show()