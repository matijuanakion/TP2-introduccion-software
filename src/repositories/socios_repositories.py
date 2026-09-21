import mysql.connector

from src.db import obtener_cursor


def _condiciones_para(filtros):
    condiciones = []
    parametros = []

    if filtros.get('nombre'):
        condiciones.append("LOWER(nombre) LIKE %s")
        parametros.append(f"%{str(filtros['nombre']).lower()}%")

    if filtros.get('activo') is not None:
        condiciones.append("activo = %s")
        parametros.append(1 if filtros['activo'] else 0)

    where = (" WHERE " + " AND ".join(condiciones)) if condiciones else ""
    return where, parametros


def obtener_socios_paginados(filtros, limit, offset):
    conexion, cursor = obtener_cursor()
    where, parametros = _condiciones_para(filtros)

    cursor.execute(
        "SELECT * FROM socios" + where +
        " ORDER BY id ASC LIMIT %s OFFSET %s",
        parametros + [limit, offset],
    )
    filas = cursor.fetchall()
    conexion.close()

    socios = []
    for fila in filas:
        socio = dict(fila)
        socio['activo'] = bool(socio['activo'])
        socios.append(socio)

    return socios


def contar_socios(filtros):
    conexion, cursor = obtener_cursor()
    where, parametros = _condiciones_para(filtros)

    cursor.execute("SELECT COUNT(*) AS cantidad FROM socios" + where, parametros)
    cantidad = cursor.fetchone()['cantidad']

    conexion.close()
    return cantidad


def obtener_socio_por_id(id_socio):
    conexion, cursor = obtener_cursor()

    try:
        cursor.execute(
            "SELECT * FROM socios WHERE id = %s",
            (id_socio,)
        )

        fila = cursor.fetchone()

        if fila is None:
            return None

        socio = dict(fila)
        socio['activo'] = bool(socio['activo'])
        return socio
    finally:
        cursor.close()
        conexion.close()


def guardar_socio(nuevo_socio):
    conexion, cursor = obtener_cursor()

    try:
        cursor.execute(
            """
            INSERT INTO socios (nombre, email, activo)
            VALUES (%s, %s, %s)
            """,
            (
                nuevo_socio['nombre'],
                nuevo_socio['email'],
                nuevo_socio['activo'],
            ),
        )
        nuevo_id = cursor.lastrowid
        conexion.commit()
    except mysql.connector.IntegrityError:
        conexion.rollback()
        return None
    finally:
        cursor.close()
        conexion.close()

    socio_guardado = dict(nuevo_socio)
    socio_guardado['id'] = nuevo_id
    return socio_guardado