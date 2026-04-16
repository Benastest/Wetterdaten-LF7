import urequests
from storage import save_json, load_json

URL = "https://api.brightsky.dev/weather?lat=52.27&lon=8.05"

def fetch_weather():
    try:
        r = urequests.get(URL)
        raw = r.json()
        r.close()

        if "weather" not in raw or len(raw["weather"]) == 0:
            print("⚠️ API liefert keine Wetterdaten!")
            return load_json("/data/cache_weather.json")

        w = raw["weather"][0]

        parsed = {
            "timestamp":      w.get("timestamp"),
            "condition":      w.get("condition"),
            "icon":           w.get("icon"),
            "temperature":    w.get("temperature"),
            "wind_speed":     w.get("wind_speed"),
            "precipitation":  w.get("precipitation"),
        }

        save_json("/data/cache_weather.json", parsed)
        return parsed

    except Exception as e:
        print("❌ API Fehler:", e)
        # Fallback
        return load_json("/data/cache_weather.json")