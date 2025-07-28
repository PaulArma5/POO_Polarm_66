# imports.py (or common imports at the top of a single file)
import tkinter as tk
from tkinter import messagebox
import threading
import time
import random # Potentially needed for simulation if not using real hardware
import sys # For checking if RPi.GPIO is available
import board # For adafruit_dht
import adafruit_dht # For DHT sensor
import telepot # For Telegram bot
from telepot.loop import MessageLoop


# --- SIMULACIÓN DE LIBRERÍAS DE HARDWARE ---
# Si no estás en una Raspberry Pi, estas clases
# simularán el comportamiento de GPIO.
# Para usar RPi.GPIO real, comenta la sección
# 'try-except ImportError' para GPIO.

try:
    import RPi.GPIO as GPIO_REAL
    print("RPi.GPIO real importado.")
    GPIO = GPIO_REAL
except ImportError:
    class MockGPIO:
        HIGH = 1
        LOW = 0
        BCM = 11
        OUT = 1

        def setmode(self, mode):
            print(f"[SIM] GPIO mode set to {mode}")

        def setup(self, pin, direction):
            print(f"[SIM] Pin {pin} setup as {'OUT' if direction == self.OUT else 'IN'}")

        def output(self, pin, state):
            status = "HIGH" if state == self.HIGH else "LOW"
            print(f"[SIM] Pin {pin} set to {status}")

        def cleanup(self):
            print("[SIM] GPIO cleanup completed.")
    GPIO = MockGPIO()
    print("RPi.GPIO no encontrado. Usando MockGPIO para simulación.")


# --- MODELO: Excepciones Personalizadas ---
# Definidas aquí para que puedan ser usadas por SensorDHTModel
class SobrecalentamientoError(Exception):
    def __init__(self, temperatura):
        super().__init__(f"¡Calentamiento detectado! Temperatura: {temperatura}°C")
        self.temperatura = temperatura

class SensorDesconectadoError(Exception):
    def __init__(self):
        super().__init__("¡El sensor DHT11 no responde o está desconectado!")

class HumedadAltaError(Exception):
    def __init__(self, humedad):
        super().__init__(f"¡Humedad extremadamente alta: {humedad}%")
        self.humedad = humedad

class HumedadBajaError(Exception):
    def __init__(self, humedad):
        super().__init__(f"¡Humedad peligrosamente baja: {humedad}%")
        self.humedad = humedad


# --- MODELO: LEDModel ---
class LEDModel:
    def __init__(self, pin=18):
        self.pin = pin
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.OUT)
            self.estado = False
            self.apagar() # Asegurarse de que el LED esté apagado al inicio
            print(f"[LEDModel]: Pin {self.pin} inicializado correctamente.")
        except Exception as e:
            print(f"LEDModel: ERROR al inicializar el pin {self.pin}: {e}")
            raise RuntimeError(f"Fallo crítico al configurar el GPIO para el LED: {e}")

    def encender(self):
        try:
            GPIO.output(self.pin, GPIO.HIGH)
            self.estado = True
            print(f"[LEDModel]: LED en pin {self.pin} ENCENDIDO.")
        except Exception as e:
            print(f"LEDModel: ERROR al encender el LED en pin {self.pin}: {e}")
            raise # Relanza la excepción para que el controlador pueda manejarla

    def apagar(self):
        try:
            GPIO.output(self.pin, GPIO.LOW)
            self.estado = False
            print(f"[LEDModel]: LED en pin {self.pin} APAGADO.")
        except Exception as e:
            print(f"LEDModel: ERROR al apagar el LED en pin {self.pin}: {e}")
            raise # Relanza la excepción para que el controlador pueda manejarla

    def obtener_estado(self):
        return self.estado

    def limpiar(self):
        try:
            GPIO.cleanup()
            print("LEDModel: GPIOs limpiados.")
        except Exception as e:
            print(f"LEDModel: ERROR al limpiar GPIO: {e}")


# --- MODELO: SensorDHTModel ---
class SensorDHTModel:
    def __init__(self, pin=board.D4):
        self.pin = pin
        self.sensor = None
        try:
            self.sensor = adafruit_dht.DHT11(self.pin)
            print(f"[SensorDHTModel]: Sensor DHT11 inicializado en pin {self.pin}.")
        except RuntimeError as e:
            print(f"[SensorDHTModel]: Error al inicializar DHT11: {e}. ¿Sensor conectado?")
            # Optionally raise a custom error or set a flag to indicate sensor failure
        except AttributeError: # Happens if board or adafruit_dht is not found/initialized
             print("[SensorDHTModel]: adafruit_dht o board no encontrado, ¿ejecutando en entorno no-RPi?")
        except Exception as e:
            print(f"[SensorDHTModel]: Error inesperado al inicializar DHT11: {e}")
            self.sensor = None # Ensure sensor is None if initialization fails


    def leer_datos(self):
        if self.sensor is None:
            raise SensorDesconectadoError("Sensor DHT no inicializado correctamente.")

        try:
            temperatura = self.sensor.temperature
            humedad = self.sensor.humidity

            if temperatura is None or humedad is None:
                raise SensorDesconectadoError() # Sensor data is None

            if temperatura > 60:
                raise SobrecalentamientoError(temperatura)

            if humedad > 90:
                raise HumedadAltaError(humedad)

            if humedad < 20:
                raise HumedadBajaError(humedad)

            return temperatura, humedad

        except RuntimeError as e: # Catch specific adafruit_dht errors
            # print(f"RuntimeError al leer DHT11: {e}") # Debugging
            raise SensorDesconectadoError() # Treat as disconnection for simplicity
        except (SobrecalentamientoError, HumedadAltaError, HumedadBajaError):
            raise # Re-raise the custom exception directly if already caught
        except Exception as e:
            print(f"[SensorDHTModel]: Error inesperado al leer datos: {e}")
            return None, None # Return None for both if another error occurs

    def limpiar(self):
        # adafruit_dht does not have a specific cleanup like GPIO
        # but if there were resources, they would be released here.
        # For now, just a print statement.
        print("[SensorDHTModel]: Limpieza del sensor DHT completada (si aplica).")


# --- VISTA: LEDView ---
class LEDView:
    def __init__(self, root):
        self.root = root
        self.root.title("LED y Sensor DHT11")

        self.label_estado = tk.Label(root, text="LED: Apagado", font=("Arial", 14))
        self.label_estado.pack(pady=10)

        self.boton = tk.Button(root, text="Encender LED", width=20, height=2, command=None)
        self.boton.pack(pady=10)

        self.label_temp = tk.Label(root, text="Temperatura: -- C", font=("Arial", 12))
        self.label_temp.pack(pady=5)

        self.label_hum = tk.Label(root, text="Humedad: -- %", font=("Arial", 12))
        self.label_hum.pack(pady=5)

        self.boton_salir = tk.Button(root, text="Salir", command=root.quit)
        self.boton_salir.pack(pady=5)

    def actualizar_estado_led(self, encendido):
        if encendido:
            self.label_estado.config(text="LED: Encendido", fg="green") # Added color for clarity
            self.boton.config(text="Apagar LED")
        else:
            self.label_estado.config(text="LED: Apagado", fg="red") # Added color for clarity
            self.boton.config(text="Encender LED")

    def actualizar_sensor(self, temp, hum):
        if temp is not None and hum is not None:
            self.label_temp.config(text=f"Temperatura: {temp}°C")
            self.label_hum.config(text=f"Humedad: {hum}%")
        else:
            self.label_temp.config(text="Temperatura: Error")
            self.label_hum.config(text="Humedad: Error")

    def asignar_controlador(self, toggle_led_func):
        self.boton.config(command=toggle_led_func)


# --- CONTROLADOR: LEDController ---
class LEDController: # Renamed from generic 'Controller' to LEDController based on main.py import
    def __init__(self, modelo_led, vista_led, sensor_dht):
        self.modelo_led = modelo_led
        self.vista_led = vista_led
        self.sensor_dht = sensor_dht # DHT Sensor Model instance

        self.bot_telegram = None # Will store the BotTelegram instance
        self.sensor_thread = None
        self.running_sensor_thread = False

        self.vista_led.asignar_controlador(self.toggle_led) # Assign LED button command
        self.vista_led.actualizar_estado_led(self.modelo_led.obtener_estado()) # Initial LED state

        # Start sensor reading in a separate thread
        self.start_sensor_reading()

    def set_bot(self, bot): # Method to set the Telegram bot instance
        self.bot_telegram = bot

    def toggle_led(self):
        try:
            if self.modelo_led.obtener_estado():
                self.modelo_led.apagar()
            else:
                self.modelo_led.encender()
            self.vista_led.actualizar_estado_led(self.modelo_led.obtener_estado())
        except Exception as e:
            print(f"Error al cambiar el estado del LED: {e}")
            messagebox.showerror("Error de Control", f"No se pudo cambiar el estado del LED: {e}")
            if self.bot_telegram:
                self.bot_telegram.enviar_mensaje_a_todos(f"Error al controlar LED: {e}")

    def start_sensor_reading(self):
        if not self.sensor_thread or not self.sensor_thread.is_alive():
            self.running_sensor_thread = True
            self.sensor_thread = threading.Thread(target=self.actualizar_sensor_periodicamente, daemon=True)
            self.sensor_thread.start()
            print("[LEDController]: Hilo de lectura de sensor iniciado.")

    def stop_sensor_reading(self):
        if self.sensor_thread and self.sensor_thread.is_alive():
            self.running_sensor_thread = False
            self.sensor_thread.join(timeout=5) # Wait for the thread to finish
            if self.sensor_thread.is_alive():
                print("[LEDController]: Advertencia: El hilo del sensor no se detuvo gracefully.")
            print("[LEDController]: Hilo de lectura de sensor detenido.")

    def actualizar_sensor_periodicamente(self):
        while self.running_sensor_thread:
            temp, hum = None, None
            try:
                temp, hum = self.sensor_dht.leer_datos()
                self.vista_led.actualizar_sensor(temp, hum)
            except SobrecalentamientoError as e:
                self.vista_led.actualizar_sensor(e.temperatura, None) # Show temp but error for hum
                if self.bot_telegram:
                    self.bot_telegram.enviar_mensaje_a_todos(f"¡ALERTA: {e}")
            except HumedadAltaError as e:
                self.vista_led.actualizar_sensor(None, e.humedad) # Show hum but error for temp
                if self.bot_telegram:
                    self.bot_telegram.enviar_mensaje_a_todos(f"¡Humedad alta detectada: {e.humedad}%")
            except HumedadBajaError as e:
                self.vista_led.actualizar_sensor(None, e.humedad) # Show hum but error for temp
                if self.bot_telegram:
                    self.bot_telegram.enviar_mensaje_a_todos(f"¡Humedad baja detectada: {e.humedad}%")
            except SensorDesconectadoError:
                self.vista_led.actualizar_sensor(None, None) # Show error for both
                if self.bot_telegram:
                    self.bot_telegram.enviar_mensaje_a_todos("Error: Sensor DHT no responde.")
            except Exception as e:
                print(f"[LEDController]: Error inesperado en hilo de sensor: {e}")
                self.vista_led.actualizar_sensor(None, None) # Show error for both
                if self.bot_telegram:
                    self.bot_telegram.enviar_mensaje_a_todos(f"Error inesperado del sensor: {e}")

            time.sleep(3) # Wait for 3 seconds before next reading

    def encender_led(self): # Helper for bot
        self.toggle_led() # Uses toggle to manage state changes

    def apagar_led(self): # Helper for bot
        self.toggle_led() # Uses toggle to manage state changes


# --- BOT: BotTelegram ---
class BotTelegram:
    def __init__(self, token, controlador):
        self.bot = telepot.Bot(token)
        self.controlador = controlador
        self.usuarios = set() # To store chat IDs of users interacting with the bot
        self.controlador.set_bot(self) # Assigns this bot instance to the controller

        MessageLoop(self.bot, self.handle).run_as_thread()
        print("Bot de Telegram en marcha...")

    def enviar_mensaje_a_todos(self, texto):
        for uid in self.usuarios:
            try:
                self.bot.sendMessage(uid, texto)
            except Exception as e:
                print(f"Error enviando mensaje a {uid}: {e}")

    def handle(self, msg):
        chat_id = msg['chat']['id']
        self.usuarios.add(chat_id) # Add user to the set of active users
        mensaje = msg.get('text', '').lower()

        if mensaje == "/on":
            self.controlador.encender_led()
            # self.bot.sendMessage(chat_id, "LED encendido") # Controller's toggle_led already handles GUI update
        elif mensaje == "/off":
            self.controlador.apagar_led()
            # self.bot.sendMessage(chat_id, "LED apagado") # Controller's toggle_led already handles GUI update
        elif mensaje == "/estado":
            estado = "encendido" if self.controlador.modelo_led.obtener_estado() else "apagado"
            self.bot.sendMessage(chat_id, f"LED está {estado}")
        elif mensaje == "/sensor":
            try:
                temp, hum = self.controlador.sensor_dht.leer_datos()
                if temp is not None:
                    self.bot.sendMessage(chat_id, f"Temperatura: {temp}°C\nHumedad: {hum}%")
                else:
                    self.bot.sendMessage(chat_id, "Error: Datos del sensor no disponibles.")
            except SensorDesconectadoError:
                self.bot.sendMessage(chat_id, "Error: Sensor DHT no responde.")
            except SobrecalentamientoError as e:
                self.bot.sendMessage(chat_id, f"¡ALERTA: {e}")
            except HumedadAltaError as e:
                self.bot.sendMessage(chat_id, f"¡Humedad alta detectada: {e.humedad}%")
            except HumedadBajaError as e:
                self.bot.sendMessage(chat_id, f"¡Humedad baja detectada: {e.humedad}%")
            except Exception as e:
                self.bot.sendMessage(chat_id, f"Error inesperado al leer sensor: {e}")
        else:
            self.bot.sendMessage(chat_id, "Comandos disponibles:\n/on\n/off\n/estado\n/sensor")


# --- FUNCIÓN PRINCIPAL ---
def main():
    modelo_led = None
    sensor_dht = None
    root = None # Initialize root to None

    try:
        root = tk.Tk()

        # Inicializar los modelos
        modelo_led = LEDModel(pin=18)
        sensor_dht = SensorDHTModel(pin=board.D4) # Use actual board pin here

        # Inicializar la vista
        vista_led = LEDView(root)

        # Inicializar el controlador
        controlador_led = LEDController(modelo_led, vista_led, sensor_dht)

        # Inicializar el bot de Telegram
        TOKEN = "7844412290:AAHMZvRMkbyGtLUntz6IxZrc3701bDPFM" # Tu token de Telegram
        # The BotTelegram constructor now assigns itself to the controller
        telegram_bot = BotTelegram(TOKEN, controlador_led)

        # Configurar protocolo de cierre para limpieza segura
        def on_closing():
            print("Cerrando aplicación desde la ventana...")
            controlador_led.stop_sensor_reading() # Stop sensor thread before exiting
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)

        root.mainloop()

    except KeyboardInterrupt:
        print("\nInterrupción por teclado.")
        messagebox.showinfo("Interrupción",
                            "Programa terminado por el usuario (Ctrl+C).")
    except RuntimeError as e: # Catch critical errors during model initialization (e.g., GPIO setup failure)
        print(f"Error crítico de inicialización: {e}")
        messagebox.showerror("Error Crítico", f"La aplicación no pudo iniciarse correctamente: {e}")
    except Exception as e:
        print(f"Error general: {e}")
        messagebox.showerror("Error General",
                              f"Ha ocurrido un error inesperado: {e}")
    finally:
        # Asegurarse de que los recursos se limpien
        if modelo_led:
            try:
                modelo_led.limpiar()
                print("GPIO limpiado correctamente.")
            except Exception as e:
                print(f"Error al intentar limpiar GPIO: {e}")

        if sensor_dht: # Ensure DHT sensor resources are cleaned up
            try:
                sensor_dht.limpiar()
                print("Sensor DHT limpiado correctamente.")
            except Exception as e:
                print(f"Error al intentar limpiar Sensor DHT: {e}")

        # Ensure sensor thread is stopped if main loop exits due to an error
        if 'controlador_led' in locals() and controlador_led.running_sensor_thread:
            controlador_led.stop_sensor_reading()
            
        print("Aplicación finalizada.")


if __name__ == "__main__":
    main()