import time
import board
import adafruit_dht
import threading
import RPi.GPIO as GPIO
import telepot
from telepot.loop import MessageLoop

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

dht_device = adafruit_dht.DHT11(board.D4)

TOKEN = '7576159730:AAF40kCysk09VM8hnM6K0QRhHS3p8GLCmL4' 
bot = telepot.Bot(TOKEN)

led_status = False

def parpadear_led():
    global led_status
    while True:
        if led_status:
            GPIO.output(18, True)
            time.sleep(1)
            GPIO.output(18, False)
            time.sleep(1)
        else:
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

def handle(msg):
    global led_status
    chat_id = msg['chat']['id']
    command = msg['text']

    if command == '/start':
        bot.sendMessage(chat_id, 'Bienvenido a este hermoso bot. Usa /Prendetepapacuichan para encender el LED y /Apagatepapacuichan para apagarlo tambien para medir temperatura usar /temp y para humedad usar /humedad')
    elif command == '/Prendetepapacuichan':
        led_status = True
        bot.sendMessage(chat_id, 'LED encendido y parpadeando por que Diosito Quiere.')
    elif command == '/Apagatepapacuichan':
        led_status = False  
        GPIO.output(18, False)  
        bot.sendMessage(chat_id, 'LED apagado y parado.')
    elif command == '/temp':
        try:
            temperatura = dht_device.temperature
            if temperatura is not None:
                bot.sendMessage(chat_id, f"Temperatura: {temperatura:.1f} °C")
            else:
                bot.sendMessage(chat_id, "Error al obtener la temperatura.")
        except RuntimeError:
            bot.sendMessage(chat_id, "Error al leer el sensor.")
    elif command == '/humedad':
        try:
            humedad = dht_device.humidity
            if humedad is not None:
                bot.sendMessage(chat_id, f"Humedad: {humedad:.1f} %")
            else:
                bot.sendMessage(chat_id, "Error al obtener la humedad.")
        except RuntimeError:
            bot.sendMessage(chat_id, "Error al leer el sensor.")
    else:
        bot.sendMessage(chat_id, 'Comando no reconocido. Usa /start para obtener ayuda.')

hilo_led = threading.Thread(target=parpadear_led)
hilo_dht = threading.Thread(target=leer_dht)

hilo_led.start()
hilo_dht.start()

MessageLoop(bot, handle).run_as_thread()

print("Bot de Telegram en funcionamiento...")
while True:
    time.sleep(10)
