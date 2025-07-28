import RPi.GPIO as GPIO
import adafruit_dht
import time
import board
from modelo.base_datos import BaseDeDatos

class SobrecalentamientoError(Exception):
    def __init__(self, temperatura):
        super().__init__(f"Sobrecalentamiento detectado! {temperatura} C")
        self.temperatura = temperatura

class SensorDesconectadoError(Exception):
    pass

class SensorDHTModel:
    def __init__(self, id_sensor, pin=board.D4):
        self.id_sensor = id_sensor
        self.sensor = adafruit_dht.DHT11(pin)
        self.db = BaseDeDatos()

    def leer_datos(self):
        try:
            temperatura = self.sensor.temperature
            humedad = self.sensor.humidity

            if temperatura is None or humedad is None:
                raise SensorDesconectadoError()

            estado = "Critico" if temperatura > 28 or humedad < 30 else "Normal"
            self.db.guardar_lectura(self.id_sensor, temperatura, humedad, estado)
            return temperatura, humedad, estado

        except SensorDesconectadoError:
            self.db.registrar_error(self.id_sensor, "Sensor desconectado")
            raise
        except Exception as e:
            self.db.registrar_error(self.id_sensor, str(e))
            raise

class LEDModel:
    def __init__(self, pin=18):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self.estado = False

    def encender(self):
        GPIO.output(self.pin, GPIO.HIGH)
        self.estado = True

    def apagar(self):
        GPIO.output(self.pin, GPIO.LOW)
        self.estado = False

    def obtener_estado(self):
        return self.estado

    def limpiar(self):
        GPIO.cleanup()
class HumedadAltaError(Exception):
    def __init__(self, humedad):
        super().__init__(f"Humedad alta detectada: {humedad}%")
        self.humedad = humedad

class HumedadBajaError(Exception):
    def __init__(self, humedad):
        super().__init__(f"Humedad baja detectada: {humedad}%")
        self.humedad = humedad


