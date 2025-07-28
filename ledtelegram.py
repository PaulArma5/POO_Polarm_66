import RPi.GPIO as GPIO
import time
from telegram.ext import Updater, CommandHandler

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

def start(update, context):
    update.message.reply_text('Bot listo. Usa /on para encender y /off para apagar.')

def turn_on(update, context):
    GPIO.output(18, True)
    update.message.reply_text('LED ENCENDIDO')

def turn_off(update, context):
    GPIO.output(18, False)
    update.message.reply_text('LED APAGADO')

TOKEN = '7576159730:AAF40kCysk09VM8hnM6K0QRhHS3p8GLCmL4'

updater = Updater(TOKEN)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("on", turn_on))
dp.add_handler(CommandHandler("off", turn_off))

updater.start_polling()
updater.idle()
