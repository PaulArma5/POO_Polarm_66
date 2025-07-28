import tkinter as tk
import tkinter.ttk as ttk

class LEDView:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor Ambiental")

        self.label_estado = tk.Label(root, text="LED: Apagado")
        self.label_estado.pack(pady=5)

        self.boton_led = tk.Button(root, text="Encender LED", command=None)
        self.boton_led.pack(pady=5)

        self.label_temp = tk.Label(root, text="Temperatura: -- C")
        self.label_temp.pack()

        self.label_hum = tk.Label(root, text="Humedad: -- %")
        self.label_hum.pack()

        self.label_alerta = tk.Label(root, text="Estado: --", fg="black")
        self.label_alerta.pack(pady=5)
        self.tree = ttk.Treeview(root, columns=("fecha", "temp", "hum", "estado"), show='headings')
        self.tree.heading("fecha", text="Fecha y Hora")
        self.tree.heading("temp", text="Temp (C)")
        self.tree.heading("hum", text="Humedad (%)")
        self.tree.heading("estado", text="Estado")
        self.tree.pack(pady=10, fill='x')

    def actualizar_estado_led(self, encendido):
        if encendido:
            self.label_estado.config(text="LED: Encendido")
            self.boton_led.config(text="Apagar LED")
        else:
            self.label_estado.config(text="LED: Apagado")
            self.boton_led.config(text="Encender LED")

    def actualizar_sensor(self, temperatura, humedad, estado):
        self.label_temp.config(text=f"Temperatura: {temperatura} C")
        self.label_hum.config(text=f"Humedad: {humedad} %")
        color = "red" if estado == "Critico" else "green"
        self.label_alerta.config(text=f"Estado: {estado}", fg=color)

    def asignar_controlador_led(self, funcion):
        self.boton_led.config(command=funcion)
    
    def actualizar_lecturas(self, lecturas):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for fila in lecturas:
            self.tree.insert("", "end", values=fila)

