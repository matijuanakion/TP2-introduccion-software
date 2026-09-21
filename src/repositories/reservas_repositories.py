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
