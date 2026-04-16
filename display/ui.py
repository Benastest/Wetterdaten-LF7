from machine import FrameBuffer, MONO_HLSB
from .oled_ssd1306 import init_display

oled = init_display()

# 16x16 Pixel Icons (MONO_HLSB Layout)

ICON_SUN = bytearray([
    0b00011000,
    0b00111100,
    0b01111110,
    0b11111111,
    0b11111111,
    0b01111110,
    0b00111100,
    0b00011000,
    0b00011000,
    0b00111100,
    0b01111110,
    0b11111111,
    0b11111111,
    0b01111110,
    0b00111100,
    0b00011000
])

ICON_CLOUD = bytearray([
    0b00000000,
    0b00011100,
    0b00111110,
    0b01111111,
    0b11111111,
    0b11111111,
    0b01111111,
    0b00111110,
    0b00011100,
    0b00000000,
    0b00000000,
    0b00000000,
    0b00000000,
    0b00000000,
    0b00000000,
    0b00000000
])

ICON_RAIN = bytearray([
    0b00000000,
    0b00011100,
    0b00111110,
    0b01111111,
    0b11111111,
    0b11111111,
    0b01111111,
    0b00111110,
    0b00011100,
    0b00000000,
    0b00100100,
    0b00000000,
    0b01001000,
    0b00000000,
    0b00100100,
    0b00000000
])


def choose_icon(condition):
    c = condition.lower()
    if "sun" in c or "clear" in c or "sonn" in c:
        return ICON_SUN
    if "rain" in c or "shower" in c or "regen" in c or "precip" in c:
        return ICON_RAIN
    return ICON_CLOUD


def draw_icon(icon_bytes, x, y):
    fb = FrameBuffer(icon_bytes, 8, 16, MONO_HLSB)
    oled.blit(fb, x, y)


def update_display(w):
    oled.fill(0)

    icon = choose_icon(w["condition"])
    draw_icon(icon, 0, 8)

    # Temperatur rechts neben dem Icon
    oled.text(f"{w['temperature']}C", 20, 0)

    # Zustand (max 10 Zeichen)
    oled.text(w["condition"][:10], 20, 12)

    # Windspeed unten
    oled.text(f"W {w['wind_speed']}m/s", 0, 24)

    oled.show()