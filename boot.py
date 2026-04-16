import network
import socket
import time

wlan = network.WLAN(network.STA_IF)
time.sleep(1)

import uasyncio as asyncio
import uos