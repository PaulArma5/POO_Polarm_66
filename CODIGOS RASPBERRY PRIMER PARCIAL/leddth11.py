import time
import board
import adafruit_dht
import threading
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

dht_device = adafruit_dht.DHT11(board.D4)  

def parpadear_led():
    while True:
        GPIO.output(18, True)
        time.sleep(1)
        GPIO.output(18, False)
        time.sleep(1)

def leer_dht():
    while True:
        try:
            temperatura = dht_device.temperature
            humedad = dht_device.humidity
            if temperatura is not None and humedad is not None:
                print(f"Temp={temperatura:.1f}C  Humedad={humedad:.1f}%")
            else:
                print("Lectura no válida.")
        except RuntimeError as error:
            print(f"Error de lectura: {error}")
        time.sleep(3)

hilo_led = threading.Thread(target=parpadear_led)
hilo_dht = threading.Thread(target=leer_dht)

hilo_led.start()
hilo_dht.start()
