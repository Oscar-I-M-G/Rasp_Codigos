import board
import digitalio
import threading
import time


button = digitalio.DigitalInOut(board.D6)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT
led_state = False

def button():
    global led_state
    while True:
        if not button.value:
            led_state = not led_state
            led.value = led_state
            time.sleep(0.2)


thread = threading.Thread(target=button)
thread.start()

while True:
    pass