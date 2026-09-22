from src.db import obtener_cursor


def existe_deporte(id_deporte):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute("SELECT COUNT(*) AS cantidad FROM deportes WHERE id = %s", (id_deporte,))
        return cursor.fetchone()['cantidad'] > 0
    finally:
        cursor.close()
        conexion.close()


def obtener_deportes():
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute("SELECT id, nombre FROM deportes ORDER BY id")
        return [dict(fila) for fila in cursor.fetchall()]
    finally:
        cursor.close()
        conexion.close()