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


def guardar_reserva(nueva_reserva):
    conexion, cursor = obtener_cursor()

    try:
        cursor.execute(
            "SELECT activo FROM socios WHERE id = %s FOR UPDATE",
            (nueva_reserva['id_socio'],),
        )
        socio = cursor.fetchone()
        if socio is None:
            conexion.rollback()
            return 'socio_inexistente'
        if not socio['activo']:
            conexion.rollback()
            return 'socio_inactivo'

        cursor.execute(
            "SELECT activa, precio_hora FROM canchas WHERE id = %s FOR UPDATE",
            (nueva_reserva['id_cancha'],),
        )
        cancha = cursor.fetchone()
        if cancha is None:
            conexion.rollback()
            return 'cancha_inexistente'
        if not cancha['activa']:
            conexion.rollback()
            return 'cancha_inactiva'

        cursor.execute(
            """
            SELECT 1
            FROM reservas
            WHERE estado NOT IN ('cancelada', 'finalizada')
              AND (id_socio = %s OR id_cancha = %s)
              AND fecha_hora_inicio < %s
              AND fecha_hora_fin > %s
            LIMIT 1
            """,
            (
                nueva_reserva['id_socio'],
                nueva_reserva['id_cancha'],
                nueva_reserva['fecha_hora_fin'],
                nueva_reserva['fecha_hora_inicio'],
            ),
        )
        if cursor.fetchone() is not None:
            conexion.rollback()
            return 'superposicion'

        precio_hora = cancha['precio_hora']
        precio_total = int(precio_hora * nueva_reserva['duracion_horas'])
        cursor.execute(
            """
            INSERT INTO reservas (
                id_socio, id_cancha, fecha_hora_inicio, fecha_hora_fin,
                estado, precio_hora, precio_total
            )
            VALUES (%s, %s, %s, %s, 'confirmada', %s, %s)
            """,
            (
                nueva_reserva['id_socio'],
                nueva_reserva['id_cancha'],
                nueva_reserva['fecha_hora_inicio'],
                nueva_reserva['fecha_hora_fin'],
                precio_hora,
                precio_total,
            ),
        )
        nueva_reserva['id'] = cursor.lastrowid
        nueva_reserva['estado'] = 'confirmada'
        nueva_reserva['precio_hora'] = precio_hora
        nueva_reserva['precio_total'] = precio_total
        nueva_reserva.pop('duracion_horas')
        conexion.commit()
        return nueva_reserva
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()
