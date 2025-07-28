import sqlite3
import os
from datetime import datetime

class BaseDeDatos:
    def __init__(self, ruta='datos/monitoreo.db'):
        os.makedirs(os.path.dirname(ruta), exist_ok=True)  
        self.conn = sqlite3.connect(ruta, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.crear_tablas()
class BaseDeDatos:
    def __init__(self, ruta='datos/monitoreo.db'):
        self.conn = sqlite3.connect(ruta, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.crear_tablas()

    def crear_tablas(self):
        self.cursor.executescript('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            correo TEXT,
            rol TEXT
        );
        CREATE TABLE IF NOT EXISTS sensores (
            id_sensor INTEGER PRIMARY KEY AUTOINCREMENT,
            ubicacion TEXT,
            tipo TEXT,
            estado TEXT
        );
        CREATE TABLE IF NOT EXISTS lecturas (
            id_lectura INTEGER PRIMARY KEY AUTOINCREMENT,
            id_sensor INTEGER,
            temperatura REAL,
            humedad REAL,
            fecha_hora TEXT,
            estado TEXT,
            FOREIGN KEY(id_sensor) REFERENCES sensores(id_sensor)
        );
        CREATE TABLE IF NOT EXISTS errores (
            id_error INTEGER PRIMARY KEY AUTOINCREMENT,
            id_sensor INTEGER,
            mensaje TEXT,
            fecha_hora TEXT,
            FOREIGN KEY(id_sensor) REFERENCES sensores(id_sensor)
        );
        ''')
        self.conn.commit()

    def guardar_lectura(self, id_sensor, temperatura, humedad, estado):
        fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('''
            INSERT INTO lecturas (id_sensor, temperatura, humedad, fecha_hora, estado)
            VALUES (?, ?, ?, ?, ?)
        ''', (id_sensor, temperatura, humedad, fecha_hora, estado))
        self.conn.commit()

    def registrar_error(self, id_sensor, mensaje):
        fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('''
            INSERT INTO errores (id_sensor, mensaje, fecha_hora)
            VALUES (?, ?, ?)
        ''', (id_sensor, mensaje, fecha_hora))
        self.conn.commit()
    def obtener_ultimas_lecturas(self, limite=10):
        self.cursor.execute('''
            SELECT fecha_hora, temperatura, humedad, estado
            FROM lecturas
            ORDER BY fecha_hora DESC
            LIMIT ?
        ''', (limite,))
        return self.cursor.fetchall()

