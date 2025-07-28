import sqlite3
import os

# Nombre del archivo de base de datos
db_filename = "escuela.db"

# Verificar si la base de datos ya existe
db_exists = os.path.exists(db_filename)

# Conectar (crea la base si no existe)
conn = sqlite3.connect(db_filename)
cursor = conn.cursor()

# Crear tablas si no existen y poblar si es nuevo
if not db_exists:
    cursor.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS carrera (
      clave_c INTEGER PRIMARY KEY,
      nom_c   TEXT,
      durac_c REAL
    );

    CREATE TABLE IF NOT EXISTS materia (
      clave_m INTEGER PRIMARY KEY,
      nom_m   TEXT,
      cred_m  REAL
    );

    CREATE TABLE IF NOT EXISTS profesor (
      clave_p INTEGER PRIMARY KEY,
      nom_p   TEXT,
      dir_p   TEXT,
      tel_p   INTEGER,
      hora_p  TEXT
    );

    CREATE TABLE IF NOT EXISTS alumno (
      mat_alu   INTEGER PRIMARY KEY,
      nom_alu   TEXT,
      edad_alu  INTEGER,
      sem_alu   INTEGER,
      gen_alu   TEXT,
      correo_alu TEXT,
      clave_c1  INTEGER,
      FOREIGN KEY (clave_c1) REFERENCES carrera (clave_c)
    );

    CREATE TABLE IF NOT EXISTS alu_pro (
      mat_alu1 INTEGER,
      clave_p1 INTEGER,
      FOREIGN KEY (mat_alu1) REFERENCES alumno (mat_alu),
      FOREIGN KEY (clave_p1) REFERENCES profesor (clave_p)
    );

    CREATE TABLE IF NOT EXISTS mat_alu (
      mat_alu2 INTEGER,
      clave_m1 INTEGER,
      FOREIGN KEY (mat_alu2) REFERENCES alumno (mat_alu),
      FOREIGN KEY (clave_m1) REFERENCES materia (clave_m)
    );

    CREATE TABLE IF NOT EXISTS mat_pro (
      clave_m2 INTEGER,
      clave_p2 INTEGER,
      FOREIGN KEY (clave_m2) REFERENCES materia (clave_m),
      FOREIGN KEY (clave_p2) REFERENCES profesor (clave_p)
    );

    INSERT INTO carrera VALUES (1, 'Ingeniería en Sistemas', 9),
                               (2, 'Ingeniería Industrial', 10);

    INSERT INTO materia VALUES (101, 'Programación', 5),
                                (102, 'Base de Datos', 4);

    INSERT INTO profesor VALUES (1, 'Dra. Ana Torres', 'Calle Falsa 123', 987654321, '2025-06-20 08:00'),
                                 (2, 'Ing. Luis Pérez', 'Av. Central 456', 987654322, '2025-06-20 09:00');

    INSERT INTO alumno VALUES (1001, 'Carlos Ramírez', 20, 4, 'Masculino', 'carlos@example.com', 1),
                               (1002, 'Lucía Díaz', 19, 3, 'Femenino', 'lucia@example.com', 2);

    INSERT INTO alu_pro VALUES (1001, 1),
                                (1002, 2);

    INSERT INTO mat_alu VALUES (1001, 101),
                                (1002, 102);

    INSERT INTO mat_pro VALUES (101, 1),
                                (102, 2);
    """)
    conn.commit()

# Consultas

print("\nConsulta 1 - Alumnos y Carreras:")
for row in cursor.execute("""
    SELECT a.nom_alu, c.nom_c
    FROM alumno a
    JOIN carrera c ON a.clave_c1 = c.clave_c;
"""):
    print(row)

print("\nConsulta 2 - Profesores y Materias:")
for row in cursor.execute("""
    SELECT p.nom_p, m.nom_m
    FROM mat_pro mp
    JOIN profesor p ON mp.clave_p2 = p.clave_p
    JOIN materia m ON mp.clave_m2 = m.clave_m;
"""):
    print(row)

print("\nConsulta 3 - Alumnos y Materias:")
for row in cursor.execute("""
    SELECT a.nom_alu, m.nom_m
    FROM mat_alu ma
    JOIN alumno a ON ma.mat_alu2 = a.mat_alu
    JOIN materia m ON ma.clave_m1 = m.clave_m;
"""):
    print(row)

conn.close()
