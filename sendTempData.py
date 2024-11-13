import time
import board
import threading
import adafruit_dht
import digitalio
import mysql.connector as mariadb
import os
from datetime import datetime


# Poniendo el sensor DHT11 en el pin 22
try:
    dht_device = adafruit_dht.DHT11(board.D22)
    print("Sensor DHT11 puesto correctamente")
except Exception as e:
    print(f"Error poniendo el sensor DHT11: {e}")
    exit()

# Configurando el boton
try:
    button = digitalio.DigitalInOut(board.D27)
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP
    print("Buton puesto correctamente")
except Exception as e:
    print(f"Error poniendo el boton: {e}")
    exit()

# configurando el LED
try:
    led = digitalio.DigitalInOut(board.D17)
    led.direction = digitalio.Direction.OUTPUT
    print("LED puesto correctamente")
except Exception as e:
    print(f"Error poniendo el LED: {e}")
    exit()
# List to store the data
temperature_data = []

# Setting up the database
db_config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'database': 'temperaturasdb'
}


# Event to stop the sensor reading
stop_sensor = threading.Event()
# Event to stop the button
stop_button = threading.Event()

#Thread safety
temperature_data_lock = threading.Lock()

def clear_screen():
    os.system('clear')

def read_dht_sensor():
    while not stop_sensor.is_set():
        try:
            temperature = dht_device.temperature
            humidity = dht_device.humidity

            if humidity is not None and temperature is not None:
                
                ahora = datetime.now()
                fecha = now.date()
                hora = now.time()
                temperature_data.append((fecha, hora, humidity, temperature))
            else:
                print("Error leyendo el sensor")
        except RuntimeError as error:
            print(error.args[0])
        time.sleep(2)

def send_data_to_db(data):
    conn = None
    cursor = None
    try:
        conn = mariadb.connect(**db_config)
        cursor = conn.cursor()
        cursor.executemany("INSERT INTO temperature_readings (FECHA, HORA, HUMEDAD, TEMPERATURA) VALUES (%s, %s,%s,%s)", data)
        conn.commit()
        print("Datos mandados correctamente")
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
            with temperature_data_lock:
                if len(temperature_data) > 0:
                    send_data_to_db(temperature_data)
                    temperature_data.clear()  # Clear the list after sending the data
            time.sleep(0.2)  # Debounce delay

sensor_thread = threading.Thread(target=read_dht_sensor)
sensor_thread.start()

# Create and start the button checking thread
button_thread = threading.Thread(target=check_button)
button_thread.start()


try:
    while True:
        with temperature_data_lock:
            print(f"Datos listos para guardar {len(temperature_data)} ")
        clear_screen()
        time.sleep(1)  # Reduce CPU usage
except KeyboardInterrupt:
    print("Saliendo del programa")
    stop_sensor.set()
    stop_button.set()
finally:
    sensor_thread.join()
    button_thread.join()
    print("Programa a terminado")