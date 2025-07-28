import tkinter as tk
from tkinter import ttk
import sqlite3
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from datetime import datetime
import unicodedata  # Para normalizar texto y quitar tildes

DB_FILE = "registros.db"

# Función para quitar tildes y normalizar texto
def quitar_tildes(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

# Crear tabla si no existe
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS registros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    piso INTEGER,
                    hora TEXT,
                    tipo TEXT)''')
conn.commit()
conn.close()

# Servidor HTTP
class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = json.loads(self.rfile.read(content_length).decode('utf-8'))

        piso = post_data.get("piso")
        tipo = post_data.get("tipo")
        hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO registros (piso, hora, tipo) VALUES (?, ?, ?)", (piso, hora, tipo))
        conn.commit()
        conn.close()

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def start_server():
    server = HTTPServer(("", 5000), RequestHandler)
    server.serve_forever()

# Interfaz gráfica
class ElevadorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Interfaz del Elevador")

        # Recuadros superiores
        tk.Label(root, text="Descripción:", bg="#b57edc", fg="white", font=("Arial", 12, "bold"), width=25).grid(row=0, column=0, padx=5, pady=5)
        tk.Label(root, text="Funcionamiento de un Elevador para Proyecto Final usando base de datos e interfaz gráfica para Programación Orientada a Objetos (POO)", wraplength=400, justify="left", bg="#e6ccf5", font=("Arial", 11), width=60).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(root, text="Número Total de Pisos:", bg="#b57edc", fg="white", font=("Arial", 12, "bold"), width=25).grid(row=1, column=0, padx=5, pady=5)
        tk.Label(root, text="3 Pisos Disponibles", bg="#e6ccf5", font=("Arial", 11), width=60).grid(row=1, column=1, padx=5, pady=5)

        # Botón colapsable
        self.caracteristicas_frame = None
        self.caracteristicas_visible = False
        self.toggle_button = tk.Button(root, text="Características:", bg="#66cc66", font=("Arial", 12, "bold"), command=self.toggle_caracteristicas)
        self.toggle_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Título de la tabla
        tk.Label(root, text="BASE DE DATOS DEL ELEVADOR", font=("Arial", 16, "bold"), fg="#004080").grid(row=3, column=0, columnspan=2, pady=(10, 0))

        # Tabla
        self.tree = ttk.Treeview(root, columns=("piso", "hora", "tipo"), show="headings")
        self.tree.heading("piso", text="Piso")
        self.tree.heading("hora", text="Hora")
        self.tree.heading("tipo", text="Tipo de Activación")
        self.tree.column("piso", width=150)
        self.tree.column("hora", width=200)
        self.tree.column("tipo", width=200)
        self.tree.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        # Botones inferiores
        resumen_btn = tk.Button(root, text="Resumen de Datos", bg="#99ccff", font=("Arial", 12, "bold"), command=self.mostrar_resumen)
        resumen_btn.grid(row=5, column=0, padx=10, pady=10)

        borrar_btn = tk.Button(root, text="Renovar Datos", bg="#99ccff", font=("Arial", 12, "bold"), command=self.borrar_datos)
        borrar_btn.grid(row=5, column=1, padx=10, pady=10)

        self.load_table()
        self.refrescar_tabla_periodicamente()

    def toggle_caracteristicas(self):
        if self.caracteristicas_visible:
            self.caracteristicas_frame.destroy()
            self.caracteristicas_visible = False
        else:
            self.caracteristicas_frame = tk.Frame(self.root, bg="#ccffcc")
            self.caracteristicas_frame.grid(row=6, column=0, columnspan=2, padx=10, pady=5)

            datos = [
                ("ELEVADOR Nº", "E - 001"),
                ("UBICACIÓN", "PARQUEADERO DEL MAZE BANK"),
                ("PESO MÁXIMO", "10 Kg"),
                ("TIPO", "USO FÍSICO Y POR CONTROL VIRTUAL"),
                ("FECHA DE INSTALACIÓN", "20/07/2025"),
                ("CAPACIDAD", "2 AUTOS Y 2 PERSONAS")
            ]

            for etiqueta, valor in datos:
                frame_dato = tk.Frame(self.caracteristicas_frame, bg="#a5e6a5", pady=3)
                frame_dato.pack(fill="x", padx=5, pady=2)
                tk.Label(frame_dato, text=f"{etiqueta}:", font=("Arial", 11, "bold"), width=25, anchor="w", bg="#a5e6a5").pack(side="left")
                tk.Label(frame_dato, text=valor, font=("Arial", 11), anchor="w", bg="#a5e6a5").pack(side="left")
            self.caracteristicas_visible = True

    def load_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT piso, hora, tipo FROM registros")
        for row in cursor.fetchall():
            piso = f"Piso Número {row[0]}"
            tipo_raw = row[2] or ""
            tipo_sin_tildes = quitar_tildes(tipo_raw).lower().strip()
            if tipo_sin_tildes == "telegram":
                tipo = "Activado por Telegram"
            elif tipo_sin_tildes == "boton" or tipo_sin_tildes == "botón":
                tipo = "Activado por Botón"
            else:
                tipo = f"Activado por {row[2]}"
            self.tree.insert("", "end", values=(piso, row[1], tipo))
        conn.close()

    def mostrar_resumen(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("SELECT piso, COUNT(*) as cantidad FROM registros GROUP BY piso ORDER BY cantidad DESC LIMIT 1")
        mas_solicitado = cursor.fetchone()
        piso_mas_solicitado = f"Piso Número {mas_solicitado[0]}" if mas_solicitado else "Sin datos"

        cursor.execute("SELECT piso, hora FROM registros ORDER BY id DESC LIMIT 1")
        ultimo = cursor.fetchone()
        ultimo_piso = f"Piso Número {ultimo[0]}" if ultimo else "Sin datos"
        hora_ultimo = ultimo[1] if ultimo else "Sin datos"

        conn.close()

        resumen = tk.Toplevel(self.root)
        resumen.title("Resumen de Datos")
        resumen.config(bg="#cce6ff")

        datos = [
            ("Piso más Solicitado", piso_mas_solicitado),
            ("Último Piso llamado", ultimo_piso),
            ("Hora del Último llamado", hora_ultimo)
        ]

        for texto, valor in datos:
            frame = tk.Frame(resumen, bg="#cce6ff", pady=3)
            frame.pack(fill="x", padx=10, pady=2)
            tk.Label(frame, text=f"{texto}:", font=("Arial", 12, "bold"), bg="#cce6ff").pack(side="left")
            tk.Label(frame, text=valor, font=("Arial", 12), bg="#cce6ff").pack(side="left")

    def borrar_datos(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM registros")
        conn.commit()
        conn.close()
        self.load_table()

    def refrescar_tabla_periodicamente(self):
        self.load_table()
        self.root.after(3000, self.refrescar_tabla_periodicamente)

if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    root = tk.Tk()
    app = ElevadorGUI(root)
    root.mainloop()
