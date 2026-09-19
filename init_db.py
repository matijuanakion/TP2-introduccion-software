import os
import sqlite3

from src.config import Config

# Nos aseguramos de que la carpeta de la base exista
os.makedirs(os.path.dirname(Config.DB_PATH), exist_ok=True)


# Conectamos a SQLite (esto crea el archivo si no existe)
conexion = sqlite3.connect(Config.DB_PATH)
cursor = conexion.cursor()

# Leemos el archivo SQL que acabamos de crear
with open(Config.DB_SCHEMA_PATH, 'r', encoding='utf-8') as archivo_sql:
    script_sql = archivo_sql.read()

# Ejecutamos todas las instrucciones juntas
cursor.executescript(script_sql)

# Guardamos los cambios y cerramos
conexion.commit()
conexion.close()

print(f"Base de datos inicializada correctamente en {Config.DB_PATH}")