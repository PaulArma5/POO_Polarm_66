import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv

DB_NAME = "escuela.db"

# ==== FUNCIONES BASE DE DATOS ====

def crear_tablas():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alumno (
            mat_alu TEXT PRIMARY KEY,
            nom_alu TEXT NOT NULL,
            edad INTEGER,
            semestre INTEGER,
            genero TEXT,
            correo TEXT,
            clave_c TEXT,
            FOREIGN KEY (clave_c) REFERENCES carrera(clave_c)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carrera (
            clave_c TEXT PRIMARY KEY,
            nom_c TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profesor (
            clave_p TEXT PRIMARY KEY,
            nom_p TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS materia (
            clave_m TEXT PRIMARY KEY,
            nom_m TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prof_mp (
            clave_p2 TEXT,
            clave_m2 TEXT,
            PRIMARY KEY (clave_p2, clave_m2),
            FOREIGN KEY (clave_p2) REFERENCES profesor(clave_p),
            FOREIGN KEY (clave_m2) REFERENCES materia(clave_m)
        )
    ''')
    conn.commit()
    conn.close()
    print("Tablas de la base de datos verificadas/creadas.")


def execute_query(query, params=()):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def fetch_query(query, params=()):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    rows = []
    columns = []
    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
    except Exception as e:
        messagebox.showerror("Error de SQL", str(e))
    finally:
        conn.close()
    return rows, columns

def show_result(frame, columns, rows):
    for widget in frame.winfo_children():
        widget.destroy()
    style = ttk.Style()
    style.configure("Treeview", rowheight=25)
    tree = ttk.Treeview(frame,
                       columns=columns, show="headings",
                       height=10)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150,
                    anchor="center")
    for row in rows:
        tree.insert("", "end", values=row)
    tree.pack(expand=True, fill='both')

    # Botón para exportar a CSV
    def export_csv():
        file = \
            filedialog.asksaveasfilename(defaultextension=".csv",
                                       filetypes=[("CSV files", "*.csv")])
        if file:
            with open(file, mode='w', newline='',
                      encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(columns) # Write headers
                writer.writerows(rows)
                messagebox.showinfo("Exportación",
                                    "Datos exportados exitosamente.")

    ttk.Button(frame, text="Exportar a CSV",
               command=export_csv).pack(pady=5)

# === FUNCIONES CRUD ===
# Asegúrate de que las variables entry_mat, etc., estén definidas globalmente o se pasen al alcance.
# Para este ejemplo, se asume que las 'entry_' variables se definen en el ámbito global del script principal.

def insertar_alumno():
    # Asume que 'entries' está disponible globalmente y sus elementos son los widgets Entry.
    # El orden en 'labels' debe coincidir con el orden de las columnas en la tabla 'alumno'.
    # Aquí se insertan 7 valores (mat_alu, nom_alu, edad, semestre, genero, correo, clave_c)
    # según la definición de `labels` y la asunción de la tabla `alumno`.
    try:
        datos = (entries[0].get(), entries[1].get(),
                 entries[2].get(), entries[3].get(),
                 entries[4].get(), entries[5].get(),
                 entries[6].get()) # 7 elementos
        query = "INSERT INTO alumno (mat_alu, nom_alu, edad, semestre, genero, correo, clave_c) VALUES (?, ?, ?, ?, ?, ?, ?)"
        execute_query(query, datos)
        messagebox.showinfo("Éxito", "Alumno insertado correctamente.")
        consultar_alumnos()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def eliminar_alumno():
    mat = entry_mat.get() # Asume entry_mat es una variable Entry global
    query = "DELETE FROM alumno WHERE mat_alu = ?"
    execute_query(query, (mat,))
    messagebox.showinfo("Éxito", "Alumno eliminado correctamente.")
    consultar_alumnos()

def consultar_alumnos():
    # Asume crud_tree es un Treeview widget global
    for row in crud_tree.get_children():
        crud_tree.delete(row)
    query = "SELECT mat_alu, nom_alu, correo_alu FROM alumno"
    rows, cols = fetch_query(query)
    for alumno_row in rows: # Iterar sobre las filas obtenidas
        crud_tree.insert('', 'end', values=alumno_row)

# === CONSULTAS PREDEFINIDAS ===
def consulta_alumnos_y_carreras():
    query = "SELECT a.nom_alu AS Alumno, c.nom_c AS Carrera FROM alumno a JOIN carrera c ON a.clave_c = c.clave_c"
    cols, rows = fetch_query(query)
    show_result(tab2_frame, cols, rows) # Asume tab2_frame existe

def consulta_profesores_y_materias():
    query = "SELECT p.nom_p AS Profesor, m.nom_m AS Materia FROM prof_mp mp JOIN profesor p ON mp.clave_p2 = p.clave_p JOIN materia m ON mp.clave_m2 = m.clave_m"
    cols, rows = fetch_query(query)
    show_result(tab3_frame, cols, rows) # Asume tab3_frame existe

def consulta_personalizada():
    query = query_text.get("1.0", tk.END).strip() # Asume query_text es un Text widget
    if not query.lower().startswith("select"):
        messagebox.showwarning("Advertencia",
                               "Solo se permiten consultas SELECT.")
        return
    cols, rows = fetch_query(query)
    show_result(tab4_frame, cols, rows) # Asume tab4_frame existe

# --- INTERFAZ GRÁFICA PRINCIPAL ---
root = tk.Tk()
root.title("Sistema de Gestión Escolar")
root.geometry("900x600")
root.configure(bg="#e6f2ff") # Color de fondo personalizado

style = ttk.Style()
style.theme_use("clam")
style.configure("TNotebook.Tab",
                padding=[10, 6], font=("Segoe UI", 10, "bold"))
style.configure("TLabel", font=("Segoe UI", 10))
style.configure("TButton", font=("Segoe UI", 10, "bold"),
                background="#006699",
                foreground="white")

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

# --- PESTAÑA 1: GESTIÓN DE ALUMNOS ---
tab1 = ttk.Frame(notebook)
form_frame = ttk.Frame(tab1, padding=10)
form_frame.pack(pady=10)

labels = ["Matricula", "Nombre", "Edad",
          "Semestre", "Género", "Correo", "Clave Carrera"]
entries = [] # Esta lista almacenará los widgets Entry

for i, label_text in enumerate(labels):
    tk.Label(form_frame, text=label_text).grid(row=i,
                                        column=0, sticky='e', padx=5, pady=5)
    entry = tk.Entry(form_frame, width=30)
    entry.grid(row=i, column=1, padx=5, pady=5)
    entries.append(entry)

# Asignar a variables específicas para fácil acceso (referenciadas en funciones CRUD)
# Estas variables deben ser accesibles por las funciones CRUD.
# Una forma simple es definirlas en el ámbito global o usar un enfoque de clase/controlador.
# Para este ejemplo de un solo archivo, las hacemos globales.
entry_mat = entries[0]
entry_nom = entries[1]
entry_edad = entries[2]
entry_sem = entries[3]
entry_gen = entries[4]
entry_correo = entries[5]
entry_carrera = entries[6]


btn_frame = ttk.Frame(form_frame)
btn_frame.grid(row=len(labels), columnspan=2,
               pady=10)

ttk.Button(btn_frame, text="Insertar",
           command=insertar_alumno).grid(row=0,
                                         column=0, padx=5)
ttk.Button(btn_frame, text="Eliminar",
           command=eliminar_alumno).grid(row=0,
                                         column=1, padx=5)
ttk.Button(btn_frame, text="Consultar",
           command=consultar_alumnos).grid(row=0,
                                           column=2, padx=5)

crud_tree = ttk.Treeview(tab1,
                         columns=("Matricula", "Nombre", "Correo"), # Columns displayed in the treeview
                         show="headings", height=10)
for col in ("Matricula", "Nombre", "Correo"):
    crud_tree.heading(col, text=col)
    crud_tree.column(col, width=200,
                     anchor="center")
crud_tree.pack(expand=True, fill='both',
               padx=10, pady=10)

notebook.add(tab1, text="Gestión de Alumnos")

# --- PESTAÑA 2: ALUMNOS Y CARRERAS ---
tab2 = ttk.Frame(notebook)
tab2_frame = ttk.Frame(tab2, padding=10)
tab2_frame.pack(expand=True, fill='both')
ttk.Button(tab2_frame, text="Mostrar Alumnos y Carreras",
           command=consulta_alumnos_y_carreras).pack(pady=5)
notebook.add(tab2, text="Alumnos - Carreras")

# === PESTAÑA 3: PROFESORES Y MATERIAS ===
tab3 = ttk.Frame(notebook)
tab3_frame = ttk.Frame(tab3, padding=10)
tab3_frame.pack(expand=True, fill='both')
ttk.Button(tab3_frame, text="Mostrar Profesores y Materias",
           command=consulta_profesores_y_materias).pack(pady=5)
notebook.add(tab3, text="Profesores - Materias")

# === PESTAÑA 4: CONSULTA LIBRE ===
tab4 = ttk.Frame(notebook)
query_text = tk.Text(tab4, height=5,
                     font=('Consolas', 10))
query_text.pack(fill='x', padx=10, pady=5)
ttk.Button(tab4, text="Ejecutar Consulta",
           command=consulta_personalizada).pack(
               pady=5)
tab4_frame = ttk.Frame(tab4, padding=10)
tab4_frame.pack(expand=True, fill='both')
notebook.add(tab4, text="Consulta Personalizada")

# --- INICIALIZACIÓN Y BUCLE PRINCIPAL ---
if __name__ == "__main__":
    crear_tablas() # Asegura que las tablas existan al iniciar
    root.mainloop()