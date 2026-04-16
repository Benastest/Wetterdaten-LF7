import time

def run_interval(seconds, callback):
    last = 0
    while True:
        now = time.time()
        if now - last >= seconds:
            callback()
            last = now
        time.sleep(0.1)