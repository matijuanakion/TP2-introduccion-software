from datetime import timedelta

from src.db import obtener_cursor


def _formatear_bloqueo(bloqueo):
    resultado = dict(bloqueo)
    if hasattr(resultado['fecha'], 'isoformat'):
        resultado['fecha'] = resultado['fecha'].isoformat()
    for campo in ('hora_inicio', 'hora_fin'):
        valor = resultado[campo]
        if isinstance(valor, timedelta):
            segundos = int(valor.total_seconds())
            horas, resto = divmod(segundos, 3600)
            minutos, segundos = divmod(resto, 60)
            resultado[campo] = f'{horas:02d}:{minutos:02d}:{segundos:02d}'
    return resultado


def _condiciones(filtros):
    condiciones = []
    parametros = []
    if filtros.get('id_cancha') is not None:
        condiciones.append('id_cancha = %s')
        parametros.append(filtros['id_cancha'])
    if filtros.get('fecha') is not None:
        condiciones.append('fecha = %s')
        parametros.append(filtros['fecha'])
    where = ' WHERE ' + ' AND '.join(condiciones) if condiciones else ''
    return where, parametros


def obtener_bloqueos(filtros, limit, offset):
    conexion, cursor = obtener_cursor()
    try:
        where, parametros = _condiciones(filtros)
        cursor.execute(
            'SELECT * FROM bloqueos' + where + ' ORDER BY id ASC LIMIT %s OFFSET %s',
            parametros + [limit, offset],
        )
        return [_formatear_bloqueo(fila) for fila in cursor.fetchall()]
    finally:
        cursor.close()
        conexion.close()


def contar_bloqueos(filtros):
    conexion, cursor = obtener_cursor()
    try:
        where, parametros = _condiciones(filtros)
        cursor.execute('SELECT COUNT(*) AS cantidad FROM bloqueos' + where, parametros)
        return cursor.fetchone()['cantidad']
    finally:
        cursor.close()
        conexion.close()


def obtener_bloqueos_en_cursor(id_cancha, fecha, cursor):
    cursor.execute(
        'SELECT * FROM bloqueos WHERE id_cancha = %s AND fecha = %s FOR UPDATE',
        (id_cancha, fecha),
    )
    return [dict(fila) for fila in cursor.fetchall()]


def guardar_bloqueo(bloqueo, conexion, cursor):
    cursor.execute(
        '''INSERT INTO bloqueos (id_cancha, fecha, hora_inicio, hora_fin, motivo)
           VALUES (%s, %s, %s, %s, %s)''',
        (bloqueo['id_cancha'], bloqueo['fecha'], bloqueo['hora_inicio'],
         bloqueo['hora_fin'], bloqueo['motivo']),
    )
    resultado = dict(bloqueo)
    resultado['id'] = cursor.lastrowid
    conexion.commit()
    return resultado


def eliminar_bloqueo(id_bloqueo):
    conexion, cursor = obtener_cursor()
    try:
        cursor.execute('DELETE FROM bloqueos WHERE id = %s', (id_bloqueo,))
        eliminado = cursor.rowcount > 0
        conexion.commit()
        return eliminado
    finally:
        cursor.close()
        conexion.close()
