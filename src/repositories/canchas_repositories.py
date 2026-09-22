from src.db import obtener_cursor


def _condiciones_para(filtros):
    condiciones = []
    parametros = []

    if filtros.get('id_deporte') is not None:
        condiciones.append("id_deporte = %s")
        parametros.append(filtros['id_deporte'])

    if filtros.get('nombre'):
        condiciones.append("LOWER(nombre) LIKE %s")
        parametros.append(f"%{str(filtros['nombre']).lower()}%")

    if filtros.get('techada') is not None:
        condiciones.append("techada = %s")
        parametros.append(1 if filtros['techada'] else 0)

    if filtros.get('activa') is not None:
        condiciones.append("activa = %s")
        parametros.append(1 if filtros['activa'] else 0)

    where = (" WHERE " + " AND ".join(condiciones)) if condiciones else ""
    return where, parametros


def obtener_canchas_paginadas(filtros, limit, offset):
    conexion, cursor = obtener_cursor()

    where, parametros = _condiciones_para(filtros)

    consulta = (
        "SELECT * FROM canchas"
        + where
        + " ORDER BY id ASC LIMIT %s OFFSET %s"
    )
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

    cursor.execute("SELECT COUNT(*) AS cantidad FROM canchas" + where, parametros)
    cantidad = cursor.fetchone()['cantidad']

    conexion.close()
    return cantidad


def obtener_canchas_para_disponibilidad(filtros):
    conexion, cursor = obtener_cursor()

    filtros_canchas = {
        campo: filtros[campo]
        for campo in ('id_deporte', 'techada')
        if filtros.get(campo) is not None
    }
    where, parametros = _condiciones_para(filtros_canchas)

    cursor.execute(
        "SELECT * FROM canchas" + where + " ORDER BY id ASC",
        parametros,
    )
    filas = cursor.fetchall()
    conexion.close()

    canchas = []
    for fila in filas:
        cancha = dict(fila)
        cancha['techada'] = bool(cancha['techada'])
        cancha['activa'] = bool(cancha['activa'])
        canchas.append(cancha)

    return canchas


def obtener_bloqueos_por_fecha(fecha):
    conexion, cursor = obtener_cursor()

    try:
        cursor.execute(
            "SELECT id_cancha, fecha, hora_inicio, hora_fin FROM bloqueos WHERE fecha = %s",
            (fecha,),
        )
        return [dict(fila) for fila in cursor.fetchall()]
    finally:
        cursor.close()
        conexion.close()


def guardar_cancha(nueva_cancha):
    conexion, cursor = obtener_cursor()

    cursor.execute("""
        INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        nueva_cancha['nombre'],
        nueva_cancha['id_deporte'],
        nueva_cancha['precio_hora'],
        nueva_cancha['techada'],
        nueva_cancha['activa']
    ))

    nuevo_id = cursor.lastrowid
    nueva_cancha['id'] = nuevo_id

    conexion.commit()
    conexion.close()

    return nueva_cancha


def obtener_cancha_por_id(id_cancha):
    conexion, cursor = obtener_cursor()

    try:
        cursor.execute(
            "SELECT * FROM canchas WHERE id = %s",
            (id_cancha,)
        )

        fila = cursor.fetchone()

        if fila is None:
            return None

        cancha = dict(fila)
        cancha['techada'] = bool(cancha['techada'])
        cancha['activa'] = bool(cancha['activa'])

        return cancha

    finally:
        cursor.close()
        conexion.close()


def actualizar_cancha(id_cancha, cancha):
    conexion, cursor = obtener_cursor()

    try:
        cursor.execute(
            """
            UPDATE canchas
            SET nombre = %s, precio_hora = %s, techada = %s, activa = %s
            WHERE id = %s
            """,
            (
                cancha['nombre'],
                cancha['precio_hora'],
                cancha['techada'],
                cancha['activa'],
                id_cancha,
            ),
        )
        conexion.commit()
    finally:
        cursor.close()
        conexion.close()


def contar_reservas_de_cancha(id_cancha):
    conexion, cursor = obtener_cursor()

    try:
        cursor.execute(
            "SELECT COUNT(*) AS cantidad FROM reservas WHERE id_cancha = %s",
            (id_cancha,),
        )
        return cursor.fetchone()['cantidad']
    finally:
        cursor.close()
        conexion.close()


def eliminar_cancha(id_cancha):
    conexion, cursor = obtener_cursor()

    try:
        cursor.execute("DELETE FROM canchas WHERE id = %s", (id_cancha,))
        conexion.commit()
    finally:
        cursor.close()
        conexion.close()