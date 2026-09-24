from src.db import obtener_cursor
from src.errores import error_respuesta
from src.repositories.bloqueos_repositories import (
    contar_bloqueos,
    eliminar_bloqueo,
    guardar_bloqueo,
    obtener_bloqueos,
    obtener_bloqueos_en_cursor,
)
from src.repositories.canchas_repositories import obtener_cancha_por_id_en_cursor
from src.repositories.reservas_repositories import obtener_reservas_relacionadas_en_cursor
from src.validators.bloqueos_validators import validar_bloqueo


def _superpuesto(inicio, fin, otro_inicio, otro_fin):
    def segundos(valor):
        horas, minutos, segundos = map(int, str(valor).split(':'))
        return horas * 3600 + minutos * 60 + segundos

    return segundos(otro_inicio) < segundos(fin) and segundos(otro_fin) > segundos(inicio)


def filtrar_bloqueos(filtros, limit, offset):
    return obtener_bloqueos(filtros, limit, offset), contar_bloqueos(filtros)


def procesar_nuevo_bloqueo(datos):
    errores, bloqueo = validar_bloqueo(datos)
    if errores:
        return {'errors': errores}, max((error.get('status', 400) for error in errores), default=400)

    conexion, cursor = obtener_cursor()
    try:
        cancha = obtener_cancha_por_id_en_cursor(bloqueo['id_cancha'], cursor)
        if cancha is None:
            conexion.rollback()
            return error_respuesta('No existe una cancha con ese id', codigo='CANCHA_INEXISTENTE'), 404
        if not cancha['activa']:
            conexion.rollback()
            return error_respuesta('La cancha no está activa', codigo='CANCHA_INACTIVA'), 409

        reservas = obtener_reservas_relacionadas_en_cursor(0, bloqueo['id_cancha'], cursor)
        if any(
            reserva['estado'] == 'confirmada'
            and str(reserva['fecha_hora_inicio'])[:10] == bloqueo['fecha']
            and _superpuesto(
                bloqueo['hora_inicio'], bloqueo['hora_fin'],
                str(reserva['fecha_hora_inicio'])[11:19],
                str(reserva['fecha_hora_fin'])[11:19],
            )
            for reserva in reservas
        ):
            conexion.rollback()
            return error_respuesta('El bloqueo se superpone con una reserva confirmada', codigo='BLOQUEO_SUPERPUESTO'), 409

        bloqueos = obtener_bloqueos_en_cursor(bloqueo['id_cancha'], bloqueo['fecha'], cursor)
        if any(_superpuesto(bloqueo['hora_inicio'], bloqueo['hora_fin'], str(item['hora_inicio']), str(item['hora_fin'])) for item in bloqueos):
            conexion.rollback()
            return error_respuesta('El bloqueo se superpone con otro bloqueo de la cancha', codigo='BLOQUEO_SUPERPUESTO'), 409

        resultado = guardar_bloqueo(bloqueo, conexion, cursor)
        return {'mensaje': 'Bloqueo creado', 'bloqueo': resultado}, 201
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def procesar_eliminacion_bloqueo(id_bloqueo):
    if not eliminar_bloqueo(id_bloqueo):
        return error_respuesta(
            f'No existe un bloqueo con id {id_bloqueo}', codigo='BLOQUEO_INEXISTENTE'
        ), 404
    return '', 204
