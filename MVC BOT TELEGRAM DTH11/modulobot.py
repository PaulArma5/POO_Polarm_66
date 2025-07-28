import time
import board
import adafruit_dht

class Sensor:
    def __init__(self):
        self.dht_device = adafruit_dht.DHT11(board.D4)
        self.temperatura = None
        self.humedad = None

    def leer_dht(self):
        try:
            self.temperatura = self.dht_device.temperature
            self.humedad = self.dht_device.humidity
            if self.temperatura is not None and self.humedad is not None:
                return f"Temp={self.temperatura:.1f}C  Humedad={self.humedad:.1f}%"
            else:
                return "Lectura no válida."
        except RuntimeError as error:
            return f"Error de lectura: {error}"
