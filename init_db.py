import sqlite3
import os

# Nos aseguramos de que la carpeta database exista
os.makedirs('database', exist_ok=True)


# Conectamos a SQLite (esto crea el archivo canchas.db si no existe)
conexion = sqlite3.connect('database/canchas.db')
cursor = conexion.cursor()

# Leemos el archivo SQL que acabamos de crear
with open('database/init_db.sql', 'r', encoding='utf-8') as archivo_sql:
    script_sql = archivo_sql.read()

# Ejecutamos todas las instrucciones juntas
cursor.executescript(script_sql)

# Guardamos los cambios y cerramos
conexion.commit()
conexion.close()

print("Base de datos inicializada correctamente en database/canchas.db")