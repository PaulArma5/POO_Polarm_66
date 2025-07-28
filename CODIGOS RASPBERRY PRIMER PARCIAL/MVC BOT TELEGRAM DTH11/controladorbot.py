import RPi.GPIO as GPIO
import time
from modulobot import Sensor
from vistabot import Vista

class Controlador:
    def __init__(self, token):
        self.sensor = Sensor()
        self.vista = Vista(token)
        self.led_status = False
        self.chat_id = None

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(18, GPIO.OUT)

    def handle(self, msg):
        self.chat_id = msg['chat']['id']
        command = msg['text']

        if command == '/start':
            self.vista.enviar_mensaje(self.chat_id, 'Bienvenido a este hermoso bot. Usa /Prendetepapacuichan para encender el LED y /Apagatepapacuichan para apagarlo, también puedes medir temperatura usando /temp y humedad usando /humedad.')
        elif command == '/Prendetepapacuichan':
            self.led_status = True
            self.vista.enviar_mensaje(self.chat_id, 'LED encendido y parpadeando por que Diosito Quiere.')
        elif command == '/Apagatepapacuichan':
            self.led_status = False
            GPIO.output(18, False)
            self.vista.enviar_mensaje(self.chat_id, 'LED apagado y parado.')
        elif command == '/temp':
            temperatura = self.sensor.leer_dht()
            self.vista.enviar_mensaje(self.chat_id, f"Temperatura: {temperatura}")
        elif command == '/humedad':
            humedad = self.sensor.leer_dht()
            self.vista.enviar_mensaje(self.chat_id, f"Humedad: {humedad}")
        else:
            self.vista.enviar_mensaje(self.chat_id, 'Comando no reconocido. Usa /start para obtener ayuda.')

    def parpadear_led(self):
        while True:
            if self.led_status:
                GPIO.output(18, True)
                time.sleep(1)
                GPIO.output(18, False)
                time.sleep(1)
            else:
                GPIO.output(18, False)
                time.sleep(1)
