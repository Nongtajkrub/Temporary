from machine import Pin
from time import sleep_ms, ticks_ms, sleep
import urequests
import json
import network

# Pir pin 5
# LED pin 25
# Button pin 27

# ชื่อของ Wifi
WIFI_SSID = ""
# รหัสผ่านของ Wifi
WIFI_PASSWORD = ""

class ButtonRisingEdge:
    def __init__(self, pin: int) -> None:
        self._button = Pin(pin, Pin.IN)
        self._old_state = False
        self._last_press_t = 0

    def is_press(self) -> bool:
        ret_val = False
        current_state = self._button.value()

        if current_state and not self._old_state:
            self._last_press_t = ticks_ms()
            ret_val = True

        self._old_state = current_state
        return ret_val

    def get_last_press_tick(self) -> int:
        return self._last_press_t

class LightingSystem:
    _pir = Pin(5, Pin.IN)
    _last_check_t = 0
    _motion_detected = False
    _motion_n = 0
    _led = Pin(25, Pin.OUT)

    @classmethod
    def loop(cls):
        motion = cls._pir.value()

        # check for movements
        if motion and not cls._motion_detected:
            cls._last_check_t = ticks_ms()
            cls._motion_detected = True
            cls._led.on()
        elif motion:
            cls._motion_n += 1

        # check every five second whether enough movements occured
        if ticks_ms() - cls._last_check_t >= 5000:
            if cls._motion_n < 5:
                cls._led.off()
                cls._motion_detected = False
            cls._last_check_t = ticks_ms()
            cls._motion_n = 0

class LineNotifySystem:
    _LINE_TOKEN = "1uZ8DJ0iAI2bCw37bzYNRnwxdvKT37Ty7wFAo88ChJxtI3jq6lkdZ3ZMY3Q6kxY9Gy7JtA2klBgtTTGiGtaspJxxE+gzbwLtNmWm2Zf+gm3awznw7vMbrFHnlTSEORzV+Q16ZUJzyOl+41BnezBz0QdB04t89/1O/w1cDnyilFU="
    _LINE_API_URL = "https://api.line.me/v2/bot/message/push"
    _LINE_GROUP_ID = "C12a9ef9eba640c491ff6d2205002c7d9"

    _button = ButtonRisingEdge(27)
    
    @classmethod
    def connect_wifi(cls):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)

        if not wlan.isconnected():
            print("Connecting to WiFi...")

            wlan.connect(cls._WIFI_SSID, cls._WIFI_PASSWORD)
            while not wlan.isconnected():
                sleep(1)

        print("Connected:", wlan.ifconfig())

    @classmethod
    def _send_message(cls, message):
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + cls._LINE_TOKEN
        }
        payload = {
            "to": cls._LINE_GROUP_ID,
            "messages": [
                {"type": "text", "text": message}
            ]
        }

        print("Sending message")
        response = urequests.post(
            cls._LINE_API_URL, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            print("Message sent")
        else:
            print("Fail to send message!")

        response.close()

    @classmethod
    def loop(cls):
        delta_time = ticks_ms() - cls._button.get_last_press_tick()

        if cls._button.is_press() and delta_time > 2000:
            cls._send_message("Help Requested!")

LineNotifySystem.connect_wifi()

while True:
    LightingSystem.loop()
    LineNotifySystem.loop()

    sleep_ms(50)
