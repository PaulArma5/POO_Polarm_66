import tkinter as tk
from modelo.modelo import LEDModel, SensorDHTModel
from vista.vista import LEDView
from controlador.controlador import LEDController

def main():
    root = tk.Tk()
    modelo_led = LEDModel()
    modelo_sensor = SensorDHTModel(id_sensor=1)
    vista = LEDView(root)
    controlador = LEDController(modelo_led, modelo_sensor, vista)

    try:
        root.mainloop()
    finally:
        modelo_led.limpiar()

if __name__ == "__main__":
    main()

