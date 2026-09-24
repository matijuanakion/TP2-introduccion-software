from src.db import obtener_cursor


def _condiciones_para(filtros):
    condiciones = []
    parametros = []

    if filtros.get('id_cancha') is not None:
        condiciones.append("id_cancha = %s")
        parametros.append(filtros['id_cancha'])

    if filtros.get('id_socio') is not None:
        condiciones.append("id_socio = %s")
        parametros.append(filtros['id_socio'])

    if filtros.get('estado') is not None:
        condiciones.append("estado = %s")
        parametros.append(filtros['estado'])

    if filtros.get('fecha_desde') is not None:
        condiciones.append("LEFT(fecha_hora_inicio, 10) >= %s")
        parametros.append(filtros['fecha_desde'])

    if filtros.get('fecha_hasta') is not None:
        condiciones.append("LEFT(fecha_hora_inicio, 10) <= %s")
        parametros.append(filtros['fecha_hasta'])

    where = (" WHERE " + " AND ".join(condiciones)) if condiciones else ""
    return where, parametros


def obtener_reservas_paginadas(filtros, limit, offset):
    conexion, cursor = obtener_cursor()

    try:
        where, parametros = _condiciones_para(filtros)
        consulta = (
            "SELECT * FROM reservas"
            + where
            + " ORDER BY id ASC LIMIT %s OFFSET %s"
        )
        cursor.execute(consulta, parametros + [limit, offset])
        return [dict(fila) for fila in cursor.fetchall()]
    finally:
        cursor.close()
        conexion.close()


def contar_reservas(filtros):
    conexion, cursor = obtener_cursor()

    try:
        where, parametros = _condiciones_para(filtros)
        cursor.execute("SELECT COUNT(*) AS cantidad FROM reservas" + where, parametros)
        return cursor.fetchone()['cantidad']
    finally:
        cursor.close()
        conexion.close()


def obtener_reservas_por_fecha(fecha):
    conexion, cursor = obtener_cursor()

    try:
        cursor.execute(
            "SELECT * FROM reservas WHERE LEFT(fecha_hora_inicio, 10) = %s",
            (fecha,),
        )
        return [dict(fila) for fila in cursor.fetchall()]
    finally:
        cursor.close()
        conexion.close()


def obtener_reservas_relacionadas(id_socio, id_cancha):
    conexion, cursor = obtener_cursor()

    try:
        cursor.execute(
            "SELECT * FROM reservas WHERE id_socio = %s OR id_cancha = %s",
            (id_socio, id_cancha),
        )
        return [dict(fila) for fila in cursor.fetchall()]
    finally:
        cursor.close()
        conexion.close()


def obtener_reservas_relacionadas_en_cursor(id_socio, id_cancha, cursor):
    cursor.execute(
        "SELECT * FROM reservas WHERE id_socio = %s OR id_cancha = %s",
        (id_socio, id_cancha),
    )
    return [dict(fila) for fila in cursor.fetchall()]


def obtener_reserva_por_id(id_reserva):
    conexion, cursor = obtener_cursor()

    try:
        cursor.execute("SELECT * FROM reservas WHERE id = %s", (id_reserva,))
        fila = cursor.fetchone()
        return dict(fila) if fila is not None else None
    finally:
        cursor.close()
        conexion.close()


def guardar_reserva(nueva_reserva):
    conexion, cursor = obtener_cursor()

    try:
        cursor.execute(
            """
            INSERT INTO reservas (
                id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin,
                estado, precio_hora, precio_total
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                nueva_reserva['id_socio'],
                nueva_reserva['id_cancha'],
                nueva_reserva['fecha_hora_inicio'],
                nueva_reserva['fecha_hora_fin'],
                nueva_reserva['estado'],
                nueva_reserva['precio_hora'],
                nueva_reserva['precio_total'],
            ),
        )
        reserva_guardada = dict(nueva_reserva)
        reserva_guardada['id'] = cursor.lastrowid
        conexion.commit()
        return reserva_guardada
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def guardar_reserva_en_transaccion(nueva_reserva, conexion, cursor):
    cursor.execute(
        """
        INSERT INTO reservas (
            id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin,
            estado, precio_hora, precio_total
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            nueva_reserva['id_socio'],
            nueva_reserva['id_cancha'],
            nueva_reserva['fecha_hora_inicio'],
            nueva_reserva['fecha_hora_fin'],
            nueva_reserva['estado'],
            nueva_reserva['precio_hora'],
            nueva_reserva['precio_total'],
        ),
    )
    reserva_guardada = dict(nueva_reserva)
    reserva_guardada['id'] = cursor.lastrowid
    conexion.commit()
    return reserva_guardada


def insertar_reserva_en_transaccion(nueva_reserva, cursor):
    cursor.execute(
        """
        INSERT INTO reservas (
            id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin,
            estado, precio_hora, precio_total
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            nueva_reserva['id_socio'],
            nueva_reserva['id_cancha'],
            nueva_reserva['fecha_hora_inicio'],
            nueva_reserva['fecha_hora_fin'],
            nueva_reserva['estado'],
            nueva_reserva['precio_hora'],
            nueva_reserva['precio_total'],
        ),
    )
    reserva_guardada = dict(nueva_reserva)
    reserva_guardada['id'] = cursor.lastrowid
    return reserva_guardada

def actualizar_estado_reserva(id_reserva, estado):
    conexion, cursor = obtener_cursor()

    try:
        cursor.execute(
            "UPDATE reservas SET estado = %s WHERE id = %s",
            (estado, id_reserva),
        )
        conexion.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conexion.close()
