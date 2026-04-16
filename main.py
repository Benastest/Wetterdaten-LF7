import time
import wifi
import server
import dwd_client
import storage

from display.oled_ssd1306 import init_display, draw_text

# --- Button Setup ---
from machine import Pin

button = Pin(15, Pin.IN, Pin.PULL_UP)
last_button_state = 1
last_switch_time = 0
screen_on = True  # Start mit eingeschaltetem Display


# OLED optional initialisieren
oled = None
try:
    oled = init_display()
except:
    print("OLED nicht gefunden – starte ohne Display.")


def safe_draw(text):
    if oled and screen_on:
        draw_text(oled, text)


def set_display_power(state: bool):
    """Display sichtbar ein-/ausschalten (SSD1306 ohne echte Power-Control)."""
    global screen_on
    screen_on = state

    if oled:
        if screen_on:
            oled.contrast(255)
            oled.fill(0)
            oled.show()
            print("Display EIN")
        else:
            oled.contrast(0)
            oled.fill(0)
            oled.show()
            print("Display AUS")


def start_webserver():
    import _thread
    _thread.start_new_thread(server.start_server, ())
    print("Webserver gestartet")


def main():

    # WLAN einmal prüfen
    safe_draw("Verbinde WLAN...")
    wlan = wifi.connect()

    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        print("WLAN aktiv:", ip)
        safe_draw("Verbunden:\n" + ip)
    else:
        print("AP aktiv unter http://192.168.4.1/")
        safe_draw("AP aktiv\n192.168.4.1")

    start_webserver()

    # Endlosschleife
    while True:
        global last_button_state, last_switch_time, screen_on

        # -------------------------
        #   🔘 BUTTON HANDLING
        # -------------------------
        current_state = button.value()

        # Button gedrückt ( = 0 ) UND entprellt
        if current_state == 0 and last_button_state == 1:
            if time.ticks_ms() - last_switch_time > 250:
                # Toggle Display
                set_display_power(not screen_on)
                last_switch_time = time.ticks_ms()

        last_button_state = current_state

        # -------------------------
        #   🌤 Wetter aktualisieren
        # -------------------------
        weather = dwd_client.fetch_weather()

        if weather:
            line1 = "{}°C {}".format(weather["temperature"], weather["condition"])
            line2 = "Wind {} m/s".format(weather["wind_speed"])
            safe_draw(line1 + "\n" + line2)

        time.sleep(10)


if __name__ == "__main__":
    main()