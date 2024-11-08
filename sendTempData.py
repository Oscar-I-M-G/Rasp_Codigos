import time
import board
import threading
import adafruit_dht
import digitalio
import mysql.connector as mariadb


# Setting up the DHT sensor
dht_device = adafruit_dht.DHT11(board.D22)

# Setting up the button
button = digitalio.DigitalInOut(board.D27)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

# Setting up the LED
led = digitalio.DigitalInOut(board.D17)
led.direction = digitalio.Direction.OUTPUT

# List to store the data
temperature_data = []

# Setting up the database
db_config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'database': 'temperaturas'
}


# Event to stop the sensor reading
stop_sensor = threading.Event()
# Event to stop the button
stop_button = threading.Event()

def read_dht_sensor():
    while not stop_sensor.is_set():
        try:
            temperature = dht_device.temperature
            humidity = dht_device.humidity

            if humidity is not None and temperature is not None:
                #print(f"Temp={temperature:.1f}C  Humidity={humidity:.1f}%")
                temperature_data.append((temperature, humidity))
            else:
                print("Failed to retrieve data from humidity sensor")
        except RuntimeError as error:
            print(error.args[0])
        time.sleep(2)

def send_data_to_db(data):
    try:
        conn = mariadb.connect(**db_config)
        cursor = conn.cursor()
        cursor.executemany("INSERT INTO temperature_readings (temperature, humidity) VALUES (%s, %s)", data)
        conn.commit()
        print("Data sent successfully")
    except mariadb.Error as err:
        print(f"Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
        time.sleep(0.5)
        led.value = False  # Turn off the LED

def check_button():
    while not stop_button.is_set():
        if not button.value:  # Button is pressed (assuming active low)
            led.value = True  # Toggle the LED
            send_data_to_db(temperature_data)
            temperature_data.clear()  # Clear the list after sending
            time.sleep(0.2)  # Debounce delay

sensor_thread = threading.Thread(target=read_dht_sensor)
sensor_thread.start()

# Create and start the button checking thread
button_thread = threading.Thread(target=check_button)
button_thread.start()


try:
    while True:
        time.sleep(1)  # Reduce CPU usage
except KeyboardInterrupt:
    print("Exiting program")
    stop_sensor.set()
    stop_button.set()
finally:
    sensor_thread.join()
    button_thread.join()
    print("Program has ended")