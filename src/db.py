import sqlite3

from src.config import Config


DB_PATH = Config.DB_PATH


def obtener_conexion():
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    return conexion


def obtener_cursor():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    return conexion, cursor