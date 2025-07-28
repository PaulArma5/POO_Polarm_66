from gpiozero import LED, Button
from time import sleep

pin_led = 18
pin_pulsador = 25

led = LED(pin_led)
pulsador = Button(pin_pulsador)

print(f"[INFO] LED configurado en GPIO {pin_led}")
print(f"[INFO] Pulsador configurado en GPIO {pin_pulsador}")
print("[INFO] Esperando pulsación...")

while True:
    if pulsador.is_pressed:
      print("[INFO] Pulsador presionado!")
      led.on()
      sleep(0.2)
      while pulsador.is_pressed:
        sleep(0.1)
      print("[INFO] Pulsador liberado.")
      led.off()
      sleep(0.5)
    else:
      led.off()
      sleep(0.1)
