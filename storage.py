import json

def save_json(path, data):
    try:
        with open(path, "w") as f:
            f.write(json.dumps(data))
    except Exception as e:
        print("❌ Fehler beim Speichern von JSON:", e)

def load_json(path):
    try:
        with open(path, "r") as f:
            return json.loads(f.read())
    except Exception as e:
        print("⚠️ Konnte JSON nicht laden:", e)
        return {}