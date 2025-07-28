import RPi.GPIO as GPIO # Importa la biblioteca para controlar los pines GPIO de Raspberry Pi
import time # Importa la biblioteca de tiempo para usar pausas

LED_PIN = 18 # Define el número del pin GPIO al que está conectado el LED (usando numeración BCM)

try:
    # Bloque para configurar GPIO y la lógica principal del programa
    GPIO.setmode(GPIO.BCM) # Establece el modo de numeración de pines a BCM (Broadcom SOC Channel)
    GPIO.setup(LED_PIN, GPIO.OUT) # Configura el pin del LED como salida

    print("Presiona Ctrl+C para salir") # Muestra una instrucción al usuario

    while True: # Bucle infinito para parpadear el LED
        GPIO.output(LED_PIN, GPIO.HIGH) # Enciende el LED (establece el pin en estado ALTO)
        print("LED encendido") # Muestra mensaje en consola
        time.sleep(1) # Espera 1 segundo

        GPIO.output(LED_PIN, GPIO.LOW) # Apaga el LED (establece el pin en estado BAJO)
        print("LED apagado") # Muestra mensaje en consola
        time.sleep(1) # Espera 1 segundo

except KeyboardInterrupt:
    # Bloque que se ejecuta si el usuario presiona Ctrl+C
    print("\nPrograma interrumpido por el usuario.")

except Exception as e:
# Bloque que captura cualquier otra excepción inesperada
    print(f"Ha ocurrido un error: {e}") # Muestra un mensaje de error con los detalles

finally:
    # Este bloque SIEMPRE se ejecuta, sin importar si hubo una excepción o no
    GPIO.cleanup() # Limpia los pines GPIO, liberando los recursos que fueron usados
    print("GPIO limpio. Programa finalizado.") # Muestra un mensaje de finalización