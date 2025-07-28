import time
import threading
from controladorbot import Controlador
from telepot.loop import MessageLoop

TOKEN = '7576159730:AAF40kCysk09VM8hnM6K0QRhHS3p8GLCmL4'

controlador = Controlador(TOKEN)

hilo_led = threading.Thread(target=controlador.parpadear_led)
hilo_led.start()

MessageLoop(controlador.vista.bot, controlador.handle).run_as_thread()

print("Bot de Telegram en funcionamiento...")
while True:
    time.sleep(10)
