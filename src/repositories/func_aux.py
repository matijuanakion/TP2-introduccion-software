import sqlite3


DB_PATH = 'database/canchas.db'


def obtener_canchas_paginadas(parametro_techada, limit, offset):
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()

    # Armamos la consulta base
    consulta = "SELECT * FROM canchas"
    parametros = []

    # Si el usuario mandó el filtro techada, lo sumamos a la consulta SQL
    if parametro_techada is not None:
        es_techada = 1 if parametro_techada.lower() == 'true' else 0
        consulta += " WHERE techada = ?"
        parametros.append(es_techada)

    # Agregamos la paginación al final de la consulta
    consulta += " LIMIT ? OFFSET ?"
    parametros.extend([limit, offset])

    # Ejecutamos la consulta dinámica
    cursor.execute(consulta, parametros)
    filas = cursor.fetchall()

    canchas = []
    for fila in filas:
        cancha_dict = dict(fila)
        cancha_dict['techada'] = bool(cancha_dict['techada'])
        cancha_dict['activa'] = bool(cancha_dict['activa'])
        canchas.append(cancha_dict)

    conexion.close()
    return canchas


def guardar_cancha(nueva_cancha):
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()

    # Fijate que NO le pasamos el 'id'. SQLite lo autoincrementa solo.
    cursor.execute("""
        INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
        VALUES (?, ?, ?, ?, ?)
    """, (
        nueva_cancha['nombre'],
        nueva_cancha['id_deporte'],
        nueva_cancha['precio_hora'],
        nueva_cancha['techada'],
        nueva_cancha['activa']
    ))

    # Le pedimos a la base de datos qué ID le asignó a la cancha recién creada
    nuevo_id = cursor.lastrowid
    nueva_cancha['id'] = nuevo_id

    conexion.commit()
    conexion.close()

    return nueva_cancha


def existe_deporte(id_deporte):
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("SELECT COUNT(*) FROM deportes WHERE id = ?", (id_deporte,))
    cantidad = cursor.fetchone()[0]
    conexion.close()
    return cantidad > 0


def obtener_deportes():
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre FROM deportes ORDER BY id")
    filas = cursor.fetchall()
    deportes = [dict(fila) for fila in filas]
    conexion.close()
    return deportes