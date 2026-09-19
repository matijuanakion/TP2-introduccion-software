import mysql.connector

from src.config import Config

# Conectamos al servidor MySQL (sin database) para crearla si no existe
conexion = mysql.connector.connect(
    host=Config.DB_HOST,
    port=Config.DB_PORT,
    user=Config.DB_USER,
    password=Config.DB_PASSWORD,
    charset='utf8mb4',
)
cursor = conexion.cursor()

# Creamos la base de datos si hace falta y la seleccionamos
cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}` CHARACTER SET utf8mb4")
cursor.execute(f"USE `{Config.DB_NAME}`")

# Leemos el archivo SQL con el schema
with open(Config.DB_SCHEMA_PATH, 'r', encoding='utf-8') as archivo_sql:
    script_sql = archivo_sql.read()

# Ejecutamos todas las instrucciones juntas
cursor.execute(script_sql)
while cursor.nextset():
    pass

# Guardamos los cambios y cerramos
conexion.commit()
conexion.close()

print(f"Base de datos '{Config.DB_NAME}' inicializada correctamente en {Config.DB_HOST}:{Config.DB_PORT}")