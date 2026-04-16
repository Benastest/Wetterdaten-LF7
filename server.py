import socket
import storage
import network
import secrets
import machine
import gc
import time


SESSION_TOKEN = None
SESSION_TIMEOUT = 3600  # 1 Stunde
SESSION_TIMESTAMP = 0


def load_template(path):
    try:
        with open(path, "r") as f:
            return f.read()
    except:
        return "<h1>Template Fehler!</h1>"


def render_template(tpl, data):
    for key in data:
        tpl = tpl.replace("{{" + key + "}}", str(data[key]))
    return tpl


def is_logged_in():
    global SESSION_TOKEN, SESSION_TIMESTAMP
    if SESSION_TOKEN and (time.time() - SESSION_TIMESTAMP) < SESSION_TIMEOUT:
        return True
    return False


def start_session():
    global SESSION_TOKEN, SESSION_TIMESTAMP
    SESSION_TOKEN = "OK"
    SESSION_TIMESTAMP = time.time()


def end_session():
    global SESSION_TOKEN
    SESSION_TOKEN = None


def parse_post(data):
    body = data.split("\r\n\r\n")[-1]
    parts = body.split("&")
    result = {}
    for p in parts:
        if "=" in p:
            k, v = p.split("=")
            result[k] = v
    return result


def start_server():
    wlan = network.WLAN(network.STA_IF)
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)

    print("Webserver läuft...")

    while True:
        cl, addr = s.accept()
        req = cl.recv(2048).decode()

        # LOGIN PAGE (GET)
        if "GET /login" in req:
            html = render_template(load_template("/web/templates/login.html"), {
                "error_msg": ""
            })
            cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
            cl.send(html)
            cl.close()
            continue

        # LOGIN PAGE (POST)
        if "POST /login" in req:
            post = parse_post(req)
            user = post.get("user", "")
            pw = post.get("pass", "")

            if user == secrets.WEBUSER and pw == secrets.WEBPASS:
                start_session()
                cl.send("HTTP/1.1 302 Found\r\nLocation: /admin\r\n\r\n")
            else:
                html = render_template(load_template("/web/templates/login.html"), {
                    "error_msg": "<p class='error'>Falsche Login-Daten!</p>"
                })
                cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
                cl.send(html)
            cl.close()
            continue

        # LOGOUT
        if "GET /logout" in req:
            end_session()
            cl.send("HTTP/1.1 302 Found\r\nLocation: /\r\n\r\n")
            cl.close()
            continue

        # ADMIN – geschützter Bereich
        if "GET /admin" in req:
            if not is_logged_in():
                cl.send("HTTP/1.1 302 Found\r\nLocation: /login\r\n\r\n")
                cl.close()
                continue

            data = {
                "wlan_ssid": wlan.config("essid") if wlan.isconnected() else "-",
                "wlan_ip": wlan.ifconfig()[0] if wlan.isconnected() else "-",
                "wlan_rssi": wlan.status("rssi") if wlan.isconnected() else "-",
                "free_ram": gc.mem_free(),
                "total_ram": gc.mem_free() + gc.mem_alloc()
            }

            html = render_template(load_template("/web/templates/admin.html"), data)
            cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
            cl.send(html)
            cl.close()
            continue

        # REBOOT
        if "GET /reboot" in req:
            cl.send("HTTP/1.1 200 OK\r\n\r\nNeustart...")
            cl.close()
            machine.reset()

        # STARTSEITE (öffentlich)
        weather = storage.load_json("/data/cache_weather.json")

        if not weather:
            weather = {
                "temperature": "?",
                "condition": "Keine Daten",
                "wind_speed": "?",
                "humidity": "?"
            }

        html = render_template(load_template("/web/templates/index.html"), weather)

        cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
        cl.send(html)
        cl.close()