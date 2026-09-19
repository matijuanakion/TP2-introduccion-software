from src.db import obtener_cursor


def existe_deporte(id_deporte):
    conexion, cursor = obtener_cursor()
    cursor.execute("SELECT COUNT(*) FROM deportes WHERE id = ?", (id_deporte,))
    cantidad = cursor.fetchone()[0]
    conexion.close()
    return cantidad > 0


def obtener_deportes():
    conexion, cursor = obtener_cursor()
    cursor.execute("SELECT id, nombre FROM deportes ORDER BY id")
    filas = cursor.fetchall()
    deportes = [dict(fila) for fila in filas]
    conexion.close()
    return deportes