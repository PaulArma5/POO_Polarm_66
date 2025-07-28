import RPi.GPIO as GPIO
import time

class Led:
    def __init__(self, pin_led):
        self.pin_led = pin_led
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin_led, GPIO.OUT)
        print(f"[INFO] LED configurado en GPIO {self.pin_led}")

    def encender(self):
        GPIO.output(self.pin_led, True)

    def apagar(self):
        GPIO.output(self.pin_led, False)

    def parpadear(self, duracion_encendido=1, duracion_apagado=1, repeticiones=None):
        print("[INFO] Iniciando parpadeo...")
        if repeticiones is None:
            while True:
                self.encender()
                time.sleep(duracion_encendido)
                self.apagar()
                time.sleep(duracion_apagado)
        else:
            for _ in range(repeticiones):
                self.encender()
                time.sleep(duracion_encendido)
                self.apagar()
                time.sleep(duracion_apagado)

pin_pulsador = 22
pin_led = 12

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin_pulsador, GPIO.IN, pull_up_down=GPIO.PUD_UP)

led = Led(pin_led)

print(f"[INFO] Pulsador configurado en GPIO {pin_pulsador}")
print("[INFO] Esperando pulsación...")

try:
    while True:
        if GPIO.input(pin_pulsador) == GPIO.LOW:
            print("[INFO] Pulsador presionado!")
            led.encender()
            time.sleep(0.2)
            while GPIO.input(pin_pulsador) == GPIO.LOW:
                time.sleep(0.1)
            print("[INFO] Pulsador liberado.")
            led.apagar()
            time.sleep(0.5)
        else:
            led.apagar()
            time.sleep(0.1)
except KeyboardInterrupt:
    print("\n[INFO] Programa terminado por el usuario.")
finally:
    GPIO.cleanup()

