import threading
import time
from modelo.modelo import SobrecalentamientoError, SensorDesconectadoError

class LEDController:
    def __init__(self, led_model, sensor_model, vista):
        self.led = led_model
        self.sensor = sensor_model
        self.vista = vista
        self.db = sensor_model.db  
        self.vista.asignar_controlador_led(self.toggle_led)
        self.iniciar_lecturas()

    def toggle_led(self):
        if self.led.obtener_estado():
            self.led.apagar()
        else:
            self.led.encender()
        self.vista.actualizar_estado_led(self.led.obtener_estado())

    def iniciar_lecturas(self):
        def loop():
            while True:
                try:
                    temp, hum, estado = self.sensor.leer_datos()
                    self.vista.actualizar_sensor(temp, hum, estado)
                    lecturas = self.db.obtener_ultimas_lecturas(10)
                    self.vista.actualizar_lecturas(lecturas)
                except Exception as e:
                    print(f"Error: {e}")
                time.sleep(5)
        threading.Thread(target=loop, daemon=True).start()


