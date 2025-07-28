import tkinter as tk
from tkinter import ttk, messagebox
import speedtest
import sqlite3
import datetime
import threading
import time
from telegram import Bot
from telegram.error import TelegramError

# Telegram config
TOKEN = "7844412290:AAHMzRVMKbiyGtLuNTZ6ixzrC370i1bDPFM"  
CHAT_ID = "229980864"

DB_PATH = "InternetSpeed.db"

# --- Funciones telegram ---
def enviar_alerta(download, upload, ping, timestamp):
    alertas = []
    if download < 5:
        alertas.append(f"📉 Descarga baja: {download} Mbps")
    if upload < 1:
        alertas.append(f"📤 Subida baja: {upload} Mbps")
    if ping > 100:
        alertas.append(f"🧱 Ping alto: {ping} ms")

    if not alertas:
        return

    mensaje = f"🚨 *Alerta de velocidad detectada*\n🕒 {timestamp}\n" + "\n".join(alertas)
    bot = Bot(token=TOKEN)
    try:
        bot.send_message(chat_id=CHAT_ID, text=mensaje, parse_mode='Markdown')
    except TelegramError as e:
        print("Error enviando mensaje a Telegram:", e)

# --- Función medir velocidad ---
def probar_velocidad():
    try:
        btn_probar.config(state="disabled")
        progress_download['value'] = 0
        progress_upload['value'] = 0
        lbl_resultado.config(text="⏳ Midiendo velocidad...")
        ventana.update()

        for i in range(0, 100, 5):
            progress_download['value'] = i
            ventana.update()
            time.sleep(0.1)

        s = speedtest.Speedtest()
        s.get_best_server()

        download = round(s.download() / 1_000_000, 2)
        progress_download['value'] = min(download, 100)
        ventana.update()

        for i in range(0, 100, 5):
            progress_upload['value'] = i
            ventana.update()
            time.sleep(0.1)

        upload = round(s.upload() / 1_000_000, 2)
        progress_upload['value'] = min(upload, 100)
        ping = s.results.ping
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lbl_resultado.config(text=f"↓ {download} Mbps | ↑ {upload} Mbps | ↔ {ping} ms\n{timestamp}")

        # Guardar en DB
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS internet_speed (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            download REAL,
            upload REAL,
            ping REAL
        )''')
        c.execute("INSERT INTO internet_speed (timestamp, download, upload, ping) VALUES (?, ?, ?, ?)",
                  (timestamp, download, upload, ping))
        conn.commit()
        conn.close()

        # Enviar alerta Telegram
        enviar_alerta(download, upload, ping, timestamp)

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo medir la velocidad:\n{e}")
        lbl_resultado.config(text="")
    finally:
        btn_probar.config(state="normal")

def medir_en_hilo():
    thread = threading.Thread(target=probar_velocidad)
    thread.start()

# --- Función cargar datos ---
def cargar_datos():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT timestamp, download, upload, ping FROM internet_speed ORDER BY id DESC LIMIT 10")
        registros = c.fetchall()
        conn.close()

        for row in tabla.get_children():
            tabla.delete(row)

        for r in registros:
            tabla.insert("", "end", values=r)

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar la base de datos:\n{e}")

# --- Contador con control para evitar sobreposición ---
def contar(boton):
    boton.config(state="disabled")
    for i in range(1, 11):
        label_contador.config(text=f"Contando: {i}")
        time.sleep(1)
    label_contador.config(text="Contador terminado")
    boton.config(state="normal")

def contar_en_hilo():
    hilo = threading.Thread(target=contar, args=(btn_contar,))
    hilo.start()

# --- GUI ---
ventana = tk.Tk()
ventana.title("WiFi Meter Realtime")
ventana.geometry("520x500")

tabs = ttk.Notebook(ventana)
tab_medicion = ttk.Frame(tabs)
tab_consultas = ttk.Frame(tabs)
tabs.add(tab_medicion, text="📶 Medir Velocidad")
tabs.add(tab_consultas, text="📋 Consultas")
tabs.pack(expand=1, fill="both")

# Medición
btn_probar = tk.Button(tab_medicion, text="Probar velocidad", font=("Arial", 14), command=medir_en_hilo)
btn_probar.pack(pady=10)

lbl_resultado = tk.Label(tab_medicion, text="", font=("Arial", 12))
lbl_resultado.pack(pady=5)

lbl_down = tk.Label(tab_medicion, text="Descarga", font=("Arial", 10))
lbl_down.pack()
progress_download = ttk.Progressbar(tab_medicion, length=300, maximum=100)
progress_download.pack(pady=5)

lbl_up = tk.Label(tab_medicion, text="Subida", font=("Arial", 10))
lbl_up.pack()
progress_upload = ttk.Progressbar(tab_medicion, length=300, maximum=100)
progress_upload.pack(pady=5)

# Contador (actividad práctica)
btn_contar = tk.Button(tab_medicion, text="Contar del 1 al 10", command=contar_en_hilo)
btn_contar.pack(pady=10)

label_contador = tk.Label(tab_medicion, text="", font=("Arial", 12))
label_contador.pack()

# Consultas
btn_cargar = tk.Button(tab_consultas, text="🔄 Cargar últimos 10 registros", command=cargar_datos)
btn_cargar.pack(pady=10)

tabla = ttk.Treeview(tab_consultas, columns=("Fecha", "Descarga", "Subida", "Ping"), show="headings")
tabla.heading("Fecha", text="Fecha")
tabla.heading("Descarga", text="↓ (Mbps)")
tabla.heading("Subida", text="↑ (Mbps)")
tabla.heading("Ping", text="↔ (ms)")
tabla.pack(padx=10, pady=10, fill="both", expand=True)

ventana.mainloop()
