import time
import board
import threading
import adafruit_dht

dht_device = adafruit_dht.DHT11(board.D4)

stop_sensor = threading.Event()

def read_dht_sensor():
    while not stop_sensor.is_set():
        try:
            temperature = dht_device.temperature
            humidity = dht_device.humidity

            if humidity is not None and temperature is not None:
                print(f"Temp={temperature:.1f}C  Humidity={humidity:.1f}%")
            else:
                print("Failed to retrieve data from humidity sensor")
        except RuntimeError as error:
            print(error.args[0])
        time.sleep(2)

thread1 = threading.Thread(target=read_dht_sensor)
thread1.start()

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting program")
    stop_sensor.set()
finally:
    thread1.join()
    print("Program has ended")