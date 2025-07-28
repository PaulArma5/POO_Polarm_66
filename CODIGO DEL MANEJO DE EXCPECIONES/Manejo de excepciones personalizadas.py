import tkinter as tk
from tkinter import messagebox

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

# --- VISTA: LEDView ---
class LEDView:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de LED")

        self.estado_label = tk.Label(root,
                                      text="LED apagado", font=("Arial", 16))
        self.estado_label.pack(pady=10)

        self.boton = tk.Button(root,
                               text="Encender", font=("Arial", 14),
                               width=15)
        self.boton.pack(pady=10)

    def actualizar_estado(self, encendido):
        if encendido:
            self.estado_label.config(text="LED encendido", fg="green")
            self.boton.config(text="Apagar")
        else:
            self.estado_label.config(text="LED apagado", fg="red")
            self.boton.config(text="Encender")

# --- CONTROLADOR: LEDController ---
class LEDController:
    def __init__(self, modelo, vista):
        self.modelo = modelo
        self.vista = vista

        self.vista.boton.config(command=self.toggle_led)

        self.vista.actualizar_estado(self.modelo.obtener_estado())

    def toggle_led(self):
        try:
            if self.modelo.obtener_estado():
                self.modelo.apagar()
            else:
                self.modelo.encender()

            self.vista.actualizar_estado(self.modelo.obtener_estado())
        except Exception as e:
            print(f"Error al cambiar el estado del LED: {e}")
            messagebox.showerror("Error de Control", f"No se pudo cambiar el estado del LED: {e}")

# --- FUNCIÓN PRINCIPAL ---
def main():
    modelo_led = None

    try:
        root = tk.Tk()

        # Inicializar el modelo del LED
        modelo_led = LEDModel(pin=18)

        # Inicializar la vista
        vista_led = LEDView(root)

        # Inicializar el controlador
        controlador_led = \
            LEDController(modelo_led, vista_led)

        # Configurar protocolo de cierre para limpieza segura
        def on_closing():
            print("Cerrando aplicación desde la ventana...")
            root.destroy()

        root.protocol("WM_DELETE_WINDOW",
                      on_closing)

        root.mainloop()

    except KeyboardInterrupt:
        print("\nInterrupción por teclado.")
        messagebox.showinfo("Interrupción",
                            "Programa terminado por el usuario (Ctrl+C).")
    except Exception as e:
        print(f"Error general: {e}")
        messagebox.showerror("Error General",
                              f"Ha ocurrido un error inesperado: {e}")
    finally:
        if modelo_led:
            try:
                modelo_led.limpiar()
                print("GPIO limpiado correctamente.")
            except Exception as e:
                print(f"Error al intentar limpiar GPIO: {e}")
        else:
            print("No se inicializa el modelo, no se limpia GPIO.")

if __name__ == "__main__":
    main()