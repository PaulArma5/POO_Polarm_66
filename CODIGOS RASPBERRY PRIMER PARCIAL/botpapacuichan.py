import RPi.GPIO as GPIO
import time
import telepot
from telepot.loop import MessageLoop

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

TOKEN = '7576159730:AAF40kCysk09VM8hnM6K0QRhHS3p8GLCmL4'
bot = telepot.Bot(TOKEN)

led_status = False

def handle(msg):
    global led_status
    chat_id = msg['chat']['id']
    command = msg['text']

    if command == '/start':
        bot.sendMessage(chat_id, 'Bienvenido a este hermoso bot usa /Prendetepapacuichan para encender el LED y /Apagatepapacuichan para apagarlo')
    elif command == '/Prendetepapacuichan':
        led_status = True
        bot.sendMessage(chat_id, 'LED encendido funcionando por que Diosito Quiere')
    elif command == '/Apagatepapacuichan':
        led_status = False
        GPIO.output(18, False)
        bot.sendMessage(chat_id, 'LED apagado ta mimido')
    else:
        bot.sendMessage(chat_id, 'Ewe usa lo que te pide >:c  /on o /off.')

MessageLoop(bot, handle).run_as_thread()

print("Bot iniciado. Usa /on para encender el LED y /off para apagarlo.")
while True:
    if led_status:
        GPIO.output(18, True)
        time.sleep(1)
        GPIO.output(18, False)
        time.sleep(1)
    else:
        GPIO.output(18, False)
        time.sleep(1)



