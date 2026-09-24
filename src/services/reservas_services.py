from datetime import datetime, timedelta, timezone

from src.db import obtener_cursor
from src.errores import error_respuesta
from src.repositories.reservas_repositories import (
    contar_reservas,
    obtener_reservas_paginadas,
    obtener_reserva_por_id,
    obtener_reservas_relacionadas_en_cursor,
    guardar_reserva_en_transaccion,
    insertar_reserva_en_transaccion,
    actualizar_estado_reserva,
)
from src.repositories.canchas_repositories import obtener_cancha_por_id_en_cursor
from src.repositories.canchas_repositories import obtener_bloqueos_relacionados_en_cursor
from src.repositories.socios_repositories import obtener_socio_por_id_en_cursor
from src.validators.reservas_validators import validar_nueva_reserva


def _fecha_hora(valor):
    return datetime.fromisoformat(str(valor).replace(' ', 'T')).replace(tzinfo=None)


def _hora_a_segundos(valor):
    horas, minutos, segundos = map(int, str(valor).split(':'))
    return horas * 3600 + minutos * 60 + segundos


def filtrar_reservas(filtros, limit, offset):
    reservas = obtener_reservas_paginadas(filtros, limit, offset)
    total = contar_reservas(filtros)
    return [_formatear_reserva(reserva) for reserva in reservas], total


def _formatear_reserva(reserva):
    reserva = dict(reserva)
    zona_horaria = timezone(timedelta(hours=-3))

    for campo in ('fecha_hora_inicio', 'fecha_hora_fin'):
        valor = reserva[campo]
        if isinstance(valor, datetime):
            fecha_hora = valor
        else:
            texto = str(valor).replace(' ', 'T')
            try:
                fecha_hora = datetime.fromisoformat(texto)
            except ValueError:
                return reserva

        if fecha_hora.tzinfo is None:
            fecha_hora = fecha_hora.replace(tzinfo=zona_horaria)
        else:
            fecha_hora = fecha_hora.astimezone(zona_horaria)
        reserva[campo] = fecha_hora.strftime('%Y-%m-%dT%H:%M:%S.%f-03:00')

    return reserva


def procesar_nueva_reserva(datos):
    errores_validacion, nueva_reserva = validar_nueva_reserva(datos)
    if errores_validacion:
        return (
            {
                'errors': [
                    {
                        'code': error['code'],
                        'message': error['message'],
                        'level': error.get('level', 'error'),
                        'description': error.get('description', error['message']),
                    }
                    for error in errores_validacion
                ]
            },
            max(
                (error.get('status', 400) for error in errores_validacion),
                default=400,
            ),
        )

    conexion, cursor = obtener_cursor()
    try:
        socio = obtener_socio_por_id_en_cursor(nueva_reserva['id_socio'], cursor)
        if socio is None:
            conexion.rollback()
            return error_respuesta(
                'No existe un socio con ese id', codigo='SOCIO_INEXISTENTE'
            ), 404
        if not socio['activo']:
            conexion.rollback()
            return error_respuesta(
                'El socio no está activo', codigo='SOCIO_INACTIVO'
            ), 409

        cancha = obtener_cancha_por_id_en_cursor(nueva_reserva['id_cancha'], cursor)
        if cancha is None:
            conexion.rollback()
            return error_respuesta(
                'No existe una cancha con ese id', codigo='CANCHA_INEXISTENTE'
            ), 404
        if not cancha['activa']:
            conexion.rollback()
            return error_respuesta(
                'La cancha no está activa', codigo='CANCHA_INACTIVA'
            ), 409

        reservas_relacionadas = obtener_reservas_relacionadas_en_cursor(
            nueva_reserva['id_socio'], nueva_reserva['id_cancha'], cursor
        )
        if any(
            reserva['estado'] == 'confirmada'
            and _fecha_hora(reserva['fecha_hora_inicio']) < _fecha_hora(nueva_reserva['fecha_hora_fin'])
            and _fecha_hora(reserva['fecha_hora_fin']) > _fecha_hora(nueva_reserva['fecha_hora_inicio'])
            for reserva in reservas_relacionadas
        ):
            conexion.rollback()
            return error_respuesta(
                'La reserva se superpone con otra reserva del socio o de la cancha',
                codigo='RESERVA_SUPERPUESTA',
            ), 409

        bloqueos = obtener_bloqueos_relacionados_en_cursor(
            nueva_reserva['id_cancha'],
            nueva_reserva['fecha_hora_inicio'][:10],
            cursor,
        )
        if any(
            _hora_a_segundos(bloqueo['hora_inicio']) < _hora_a_segundos(nueva_reserva['fecha_hora_fin'][11:19])
            and _hora_a_segundos(bloqueo['hora_fin']) > _hora_a_segundos(nueva_reserva['fecha_hora_inicio'][11:19])
            for bloqueo in bloqueos
        ):
            conexion.rollback()
            return error_respuesta(
                'La reserva se superpone con un bloqueo de mantenimiento',
                codigo='RESERVA_SUPERPUESTA',
            ), 409

        nueva_reserva['estado'] = 'confirmada'
        nueva_reserva['precio_hora'] = cancha['precio_hora']
        nueva_reserva['precio_total'] = int(
            cancha['precio_hora'] * nueva_reserva.pop('duracion_horas')
        )
        resultado = guardar_reserva_en_transaccion(nueva_reserva, conexion, cursor)
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()

    return {'mensaje': 'Reserva creada', 'reserva': resultado}, 201


def procesar_reservas_recurrentes(datos):
    from src.repositories.canchas_repositories import obtener_bloqueos_relacionados_en_cursor
    from src.validators.reservas_validators import validar_reserva_recurrente

    errores, cantidad = validar_reserva_recurrente(datos)
    if errores:
        return {'errors': errores}, max((error.get('status', 400) for error in errores), default=400)

    inicio = datetime.strptime(datos['fecha_hora_inicio'], '%Y-%m-%dT%H:%M:%S.%f-03:00')
    fin = datetime.strptime(datos['fecha_hora_fin'], '%Y-%m-%dT%H:%M:%S.%f-03:00')
    candidatos = []
    conflictos = []
    for semana in range(cantidad):
        desplazamiento = timedelta(weeks=semana)
        inicio_semana = inicio + desplazamiento
        fin_semana = fin + desplazamiento
        payload = {
            'id_socio': datos['id_socio'],
            'id_cancha': datos['id_cancha'],
            'fecha_hora_inicio': inicio_semana.strftime('%Y-%m-%dT%H:%M:%S.%f-03:00'),
            'fecha_hora_fin': fin_semana.strftime('%Y-%m-%dT%H:%M:%S.%f-03:00'),
        }
        errores_semana, reserva = validar_nueva_reserva(payload)
        if errores_semana:
            conflictos.append(payload['fecha_hora_inicio'][:10])
        else:
            candidatos.append(reserva)

    if conflictos:
        return {
            'errors': [{'code': 'RESERVAS_RECURRENTES_INVALIDAS',
                        'message': 'Una o más fechas de la serie no son válidas',
                        'level': 'error',
                        'description': 'La serie no fue creada'}],
            'conflictos': sorted(set(conflictos)),
        }, 409

    conexion, cursor = obtener_cursor()
    try:
        socio = obtener_socio_por_id_en_cursor(datos['id_socio'], cursor)
        if socio is None:
            conexion.rollback()
            return error_respuesta('No existe un socio con ese id', codigo='SOCIO_INEXISTENTE'), 404
        if not socio['activo']:
            conexion.rollback()
            return error_respuesta('El socio no está activo', codigo='SOCIO_INACTIVO'), 409
        cancha = obtener_cancha_por_id_en_cursor(datos['id_cancha'], cursor)
        if cancha is None:
            conexion.rollback()
            return error_respuesta('No existe una cancha con ese id', codigo='CANCHA_INEXISTENTE'), 404
        if not cancha['activa']:
            conexion.rollback()
            return error_respuesta('La cancha no está activa', codigo='CANCHA_INACTIVA'), 409

        relacionadas = obtener_reservas_relacionadas_en_cursor(datos['id_socio'], datos['id_cancha'], cursor)
        for reserva in candidatos:
            if any(
                existente['estado'] == 'confirmada'
                and _fecha_hora(existente['fecha_hora_inicio']) < _fecha_hora(reserva['fecha_hora_fin'])
                and _fecha_hora(existente['fecha_hora_fin']) > _fecha_hora(reserva['fecha_hora_inicio'])
                for existente in relacionadas
            ):
                conflictos.append(reserva['fecha_hora_inicio'][:10])
            bloqueos = obtener_bloqueos_relacionados_en_cursor(datos['id_cancha'], reserva['fecha_hora_inicio'][:10], cursor)
            if any(
                _hora_a_segundos(bloqueo['hora_inicio']) < _hora_a_segundos(reserva['fecha_hora_fin'][11:19])
                and _hora_a_segundos(bloqueo['hora_fin']) > _hora_a_segundos(reserva['fecha_hora_inicio'][11:19])
                for bloqueo in bloqueos
            ):
                conflictos.append(reserva['fecha_hora_inicio'][:10])
        if conflictos:
            conexion.rollback()
            return {
                'errors': [{'code': 'RESERVA_SUPERPUESTA',
                            'message': 'Una o más fechas de la serie no están disponibles',
                            'level': 'error',
                            'description': 'La serie no fue creada'}],
                'conflictos': sorted(set(conflictos)),
            }, 409

        guardadas = []
        for reserva in candidatos:
            reserva['estado'] = 'confirmada'
            reserva['precio_hora'] = cancha['precio_hora']
            reserva['precio_total'] = int(cancha['precio_hora'] * reserva.pop('duracion_horas'))
            guardadas.append(insertar_reserva_en_transaccion(reserva, cursor))
        conexion.commit()
        return {'mensaje': 'Reservas recurrentes creadas', 'reservas': guardadas}, 201
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def consultar_reserva(id_reserva):
    reserva = obtener_reserva_por_id(id_reserva)
    if reserva is None:
        return error_respuesta(
            f'No existe una reserva con id {id_reserva}',
            codigo='RESERVA_INEXISTENTE',
        ), 404
    return _formatear_reserva(reserva), 200


def procesar_estado_reserva(id_reserva, estado):
    reserva = obtener_reserva_por_id(id_reserva)
    if reserva is None:
        return error_respuesta(
            f'No existe una reserva con id {id_reserva}',
            codigo='RESERVA_INEXISTENTE',
        ), 404

    if estado == reserva['estado']:
        return '', 204

    inicio = _fecha_hora(reserva['fecha_hora_inicio'])
    fin = _fecha_hora(reserva['fecha_hora_fin'])
    ahora = datetime.now(timezone(timedelta(hours=-3))).replace(tzinfo=None)

    permitido = (
        reserva['estado'] == 'confirmada'
        and (
            (estado == 'cancelada' and ahora < inicio)
            or (estado == 'finalizada' and ahora >= fin)
        )
    )
    if not permitido:
        return error_respuesta(
            f'No se puede cambiar una reserva de {reserva["estado"]} a {estado}',
            codigo='TRANSICION_ESTADO_INVALIDA',
        ), 409

    actualizar_estado_reserva(id_reserva, estado)
    return '', 204
