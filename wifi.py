# wifi.py – WLAN + Hotspot + AP-Fallback mit WiFi-Hardware-Reset

import network
import time
from secrets import WIFI_CREDENTIALS

AP_SSID = "ESP32_Fallback"
AP_PASSWORD = "12345678"


def reset_wifi_hardware():
    """Hard-Reset der WiFi-Hardware. Fix für iPhone-Hotspot-Fehler."""
    print("🔄 WLAN-Hardware Reset...")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    time.sleep(1)
    wlan.active(True)
    time.sleep(1)
    print("✅ WLAN Reset abgeschlossen.")
    return wlan


def connect_sta():
    """Verbindet zu den WLANs aus WIFI_CREDENTIALS."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # Wenn bereits verbunden
    if wlan.isconnected():
        return wlan

    for cred in WIFI_CREDENTIALS:
        ssid = cred["ssid"]
        pw = cred["password"]

        print(f"🔍 Versuche WLAN: {ssid}")

        try:
            wlan.connect(ssid, pw)

            for _ in range(20):
                if wlan.isconnected():
                    print(f"✅ Verbunden mit {ssid}, IP:", wlan.ifconfig()[0])
                    return wlan
                time.sleep(0.5)

            print(f"❌ Verbindung zu {ssid} fehlgeschlagen\n")

        except OSError as e:
            print("❌ OSError beim Verbinden:", e)
            wlan = reset_wifi_hardware()

    return wlan


def start_ap():
    """Startet einen eigenen Access Point als Fallback."""
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=AP_SSID, password=AP_PASSWORD, authmode=3)

    print("📡 AP-Fallback aktiv!")
    print("➡ SSID:", AP_SSID)
    print("➡ Passwort:", AP_PASSWORD)
    print("➡ IP: 192.168.4.1")
    return ap


def connect():
    """Hauptfunktion: STA → (Fehler Reset) → AP"""
    wlan = connect_sta()

    # STA erfolgreich?
    if wlan.isconnected():
        return wlan

    print("⚠️ Kein WLAN möglich → starte AP-Fallback...")
    start_ap()
    return wlan