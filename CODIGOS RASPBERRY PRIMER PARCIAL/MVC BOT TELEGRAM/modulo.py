import RPi.GPIO as GPIO
import time

class LEDModel:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self.led_status = False

    def turn_on(self):
        self.led_status = True
        GPIO.output(self.pin, True)

    def turn_off(self):
        self.led_status = False
        GPIO.output(self.pin, False)

    def blink(self):
        while self.led_status:
            GPIO.output(self.pin, True)
            time.sleep(0)
            GPIO.output(self.pin, False)
            time.sleep(0)

    def stop_blinking(self):
        self.turn_off()
