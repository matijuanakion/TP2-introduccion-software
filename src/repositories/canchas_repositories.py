from src.db import obtener_cursor


def _condiciones_para(filtros):
    condiciones = []
    parametros = []

    if filtros.get('id_deporte') is not None:
        condiciones.append("id_deporte = ?")
        parametros.append(filtros['id_deporte'])

    if filtros.get('nombre'):
        condiciones.append("LOWER(nombre) LIKE ?")
        parametros.append(f"%{str(filtros['nombre']).lower()}%")

    if filtros.get('techada') is not None:
        condiciones.append("techada = ?")
        parametros.append(1 if filtros['techada'] else 0)

    if filtros.get('activa') is not None:
        condiciones.append("activa = ?")
        parametros.append(1 if filtros['activa'] else 0)

    where = (" WHERE " + " AND ".join(condiciones)) if condiciones else ""
    return where, parametros


def obtener_canchas_paginadas(filtros, limit, offset):
    conexion, cursor = obtener_cursor()

    where, parametros = _condiciones_para(filtros)

    # Agregamos la paginación al final de la consulta
    consulta = "SELECT * FROM canchas" + where + " LIMIT ? OFFSET ?"
    parametros.extend([limit, offset])

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


def contar_canchas(filtros):
    conexion, cursor = obtener_cursor()

    where, parametros = _condiciones_para(filtros)

    cursor.execute("SELECT COUNT(*) FROM canchas" + where, parametros)
    cantidad = cursor.fetchone()[0]

    conexion.close()
    return cantidad


def guardar_cancha(nueva_cancha):
    conexion, cursor = obtener_cursor()

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