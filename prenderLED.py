import board
import digitalio
import threading
import time

led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT


def blink_led():
    while True:
        led.value = not led.value
        time.sleep(0.5)
    


thread = threading.Thread(target=blink_led)
thread.start()
while True:
    pass

