import RPi.GPIO as GPIO
import adafruit_dht
import board
import time
import threading

# Pines
PIN_DHT = 4
PIN_LLUVIA = 17
PIN_HUMEDAD = 27  
PIN_BUZZER = 22

# Configuración GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_LLUVIA, GPIO.IN)
GPIO.setup(PIN_HUMEDAD, GPIO.IN)
GPIO.setup(PIN_BUZZER, GPIO.OUT)

# Sensor DHT11
sensor_dht = adafruit_dht.DHT11(board.D4)

# Excepciones personalizadas
class SensorException(Exception): pass
class TemperaturaAlta(SensorException): pass
class HumedadAlta(SensorException): pass
class SueloSeco(SensorException): pass

# Variables globales compartidas
datos = {
    "humedad_suelo": None,
    "lluvia": None,
    "temperatura": None,
    "humedad": None,
    "buzzer_activo": False
}

# Función para leer sensores
def leer_sensores():
    humedad_suelo = GPIO.input(PIN_HUMEDAD)
    lluvia = GPIO.input(PIN_LLUVIA)
    temp, hum = None, None

    for _ in range(3):  # Hasta 3 intentos
        try:
            temp = sensor_dht.temperature
            hum = sensor_dht.humidity
            break
        except RuntimeError as e:
            print(f"[WARN] Reintentando DHT11: {e}")
            time.sleep(0.5)
        except Exception as e:
            print(f"[ERROR] Falla grave en DHT11: {e}")
            break

    # Evaluar condiciones
    condiciones_criticas = (
        humedad_suelo == 1 or     # Suelo seco
        lluvia == 0 or            # Está lloviendo
        (temp is not None and temp > 35) or
        (hum is not None and hum < 20)
    )

    if condiciones_criticas:
        activar_buzzer()
    else:
        desactivar_buzzer()

    # Guardar datos globales
    datos["humedad_suelo"] = humedad_suelo
    datos["lluvia"] = lluvia
    datos["temperatura"] = temp
    datos["humedad"] = hum

    return humedad_suelo, lluvia, temp, hum

def verificar_excepciones(temp, hum, suelo):
    if temp is not None and temp >= 35:
        raise TemperaturaAlta("Temperatura mayor a 35°C")
    if hum is not None and hum >= 85:
        raise HumedadAlta("Humedad mayor a 85%")
    if suelo == 1:
        raise SueloSeco("El suelo está seco")

def activar_buzzer():
    GPIO.output(PIN_BUZZER, GPIO.HIGH)
    datos["buzzer_activo"] = True

def desactivar_buzzer():
    GPIO.output(PIN_BUZZER, GPIO.LOW)
    datos["buzzer_activo"] = False

def limpiar_gpio():
    GPIO.cleanup()

# Hilo para actualización automática
def iniciar_actualizacion_automatica(intervalo=5):
    def actualizar():
        while True:
            try:
                leer_sensores()
            except Exception as e:
                print(f"[ERROR] Error en actualización automática: {e}")
            time.sleep(intervalo)

    hilo = threading.Thread(target=actualizar, daemon=True)
    hilo.start()