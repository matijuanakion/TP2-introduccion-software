import mysql.connector

from src.config import Config


def obtener_conexion():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset='utf8mb4',
    )


def obtener_cursor():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    return conexion, cursor