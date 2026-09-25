from datetime import datetime

from src.db import obtener_cursor
from src.errores import error_respuesta
from src.repositories.canchas_repositories import (
    obtener_cancha_por_id,
    obtener_canchas_paginadas,
    contar_canchas,
    guardar_cancha,
    actualizar_cancha,
    obtener_cancha_por_id_en_cursor,
    contar_reservas_de_cancha_en_cursor,
    eliminar_cancha_en_transaccion,
    obtener_canchas_para_disponibilidad,
    obtener_bloqueos_por_fecha,
)
from src.repositories.reservas_repositories import obtener_reservas_por_fecha
from src.validators.canchas_validators import (
    validar_actualizacion_cancha,
    validar_nueva_cancha,
)


def filtrar_canchas(filtros, limit, offset):
    canchas = obtener_canchas_paginadas(filtros, limit, offset)
    total = contar_canchas(filtros)
    return canchas, total


def filtrar_canchas_disponibles(filtros, limit, offset):
    canchas = obtener_canchas_para_disponibilidad(filtros)
    reservas = obtener_reservas_por_fecha(filtros['fecha'])
    bloqueos = obtener_bloqueos_por_fecha(filtros['fecha'])
    inicio = f"{filtros['fecha']} {filtros['hora_inicio']}"
    fin = f"{filtros['fecha']} {filtros['hora_fin']}"
    inicio = datetime.fromisoformat(inicio)
    fin = datetime.fromisoformat(fin)

    def segundos(valor):
        horas, minutos, segundos_hora = map(int, str(valor).split(':'))
        return horas * 3600 + minutos * 60 + segundos_hora

    def se_superpone(intervalo_inicio, intervalo_fin):
        reserva_inicio = datetime.fromisoformat(str(intervalo_inicio).replace(' ', 'T'))
        reserva_fin = datetime.fromisoformat(str(intervalo_fin).replace(' ', 'T'))
        return reserva_inicio < fin and reserva_fin > inicio

    canchas_disponibles = []
    for cancha in canchas:
        if not cancha['activa']:
            continue

        tiene_reserva = any(
            reserva['estado'] == 'confirmada'
            and reserva['id_cancha'] == cancha['id']
            and se_superpone(
                str(reserva['fecha_hora_inicio']),
                str(reserva['fecha_hora_fin']),
            )
            for reserva in reservas
        )
        tiene_bloqueo = any(
            bloqueo['id_cancha'] == cancha['id']
            and segundos(bloqueo['hora_inicio']) < segundos(filtros['hora_fin'])
            and segundos(bloqueo['hora_fin']) > segundos(filtros['hora_inicio'])
            for bloqueo in bloqueos
        )
        if not tiene_reserva and not tiene_bloqueo:
            canchas_disponibles.append(cancha)

    return canchas_disponibles[offset:offset + limit], len(canchas_disponibles)


def procesar_nueva_cancha(datos):
    errores, nueva_cancha = validar_nueva_cancha(datos)

    if errores:
        return (
            {
                "errors": [
                    {
                        "code": error["code"],
                        "message": error["message"],
                        "level": error.get("level", "error"),
                        "description": error.get("description", error["message"]),
                    }
                    for error in errores
                ]
            },
            max((error.get("status", 400) for error in errores), default=400),
        )

    cancha_guardada = guardar_cancha(nueva_cancha)

    return {"mensaje": "Cancha creada", "cancha": cancha_guardada}, 201


def consultar_cancha(id_cancha):
    cancha = obtener_cancha_por_id(id_cancha)

    if cancha is None:
        return error_respuesta(
            f"No existe una cancha con id {id_cancha}",
            codigo="CANCHA_INEXISTENTE",
        ), 404

    return cancha, 200


def procesar_actualizacion_cancha(id_cancha, datos):
    campos_no_editables = set(datos) - {'nombre', 'precio_hora', 'techada', 'activa'}
    if not datos or campos_no_editables:
        return error_respuesta(
            'Debe indicarse al menos un campo editable y no incluir campos desconocidos',
            codigo='CUERPO_INVALIDO',
        ), 400

    cancha_actual = obtener_cancha_por_id(id_cancha)

    if cancha_actual is None:
        return error_respuesta(
            f"No existe una cancha con id {id_cancha}",
            codigo="CANCHA_INEXISTENTE",
        ), 404

    errores, cancha_actualizada = validar_actualizacion_cancha(datos, cancha_actual)

    if errores:
        return (
            {
                "errors": [
                    {
                        "code": error["code"],
                        "message": error["message"],
                        "level": error.get("level", "error"),
                        "description": error.get("description", error["message"]),
                    }
                    for error in errores
                ]
            },
            max((error.get("status", 400) for error in errores), default=400),
        )

    actualizar_cancha(id_cancha, cancha_actualizada)
    cancha_actualizada['id'] = id_cancha
    return cancha_actualizada, 200


def procesar_eliminacion_cancha(id_cancha):
    conexion, cursor = obtener_cursor()
    try:
        cancha = obtener_cancha_por_id_en_cursor(id_cancha, cursor)
        if cancha is None:
            conexion.rollback()
            return error_respuesta(
                f"No existe una cancha con id {id_cancha}",
                codigo="CANCHA_INEXISTENTE",
            ), 404

        if contar_reservas_de_cancha_en_cursor(id_cancha, cursor) > 0:
            conexion.rollback()
            return error_respuesta(
                f"No se puede eliminar la cancha con id {id_cancha} porque tiene reservas asociadas",
                codigo="CANCHA_CON_RESERVAS",
            ), 409

        eliminar_cancha_en_transaccion(id_cancha, conexion, cursor)
        return "", 204
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()