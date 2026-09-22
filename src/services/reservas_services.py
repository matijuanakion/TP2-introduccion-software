from datetime import datetime, timedelta, timezone

from src.errores import error_respuesta
from src.repositories.reservas_repositories import (
    contar_reservas,
    guardar_reserva,
    obtener_reservas_paginadas,
    obtener_reserva_por_id,
    obtener_reservas_relacionadas,
    actualizar_estado_reserva,
)
from src.repositories.canchas_repositories import obtener_cancha_por_id
from src.repositories.socios_repositories import obtener_socio_por_id
from src.validators.reservas_validators import validar_nueva_reserva


def _fecha_hora(valor):
    return datetime.fromisoformat(str(valor).replace(' ', 'T')).replace(tzinfo=None)


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

    socio = obtener_socio_por_id(nueva_reserva['id_socio'])
    if socio is None:
        return error_respuesta(
            'No existe un socio con ese id', codigo='SOCIO_INEXISTENTE'
        ), 404
    if not socio['activo']:
        return error_respuesta(
            'El socio no está activo', codigo='SOCIO_INACTIVO'
        ), 409

    cancha = obtener_cancha_por_id(nueva_reserva['id_cancha'])
    if cancha is None:
        return error_respuesta(
            'No existe una cancha con ese id', codigo='CANCHA_INEXISTENTE'
        ), 404
    if not cancha['activa']:
        return error_respuesta(
            'La cancha no está activa', codigo='CANCHA_INACTIVA'
        ), 409

    reservas_relacionadas = obtener_reservas_relacionadas(
        nueva_reserva['id_socio'], nueva_reserva['id_cancha']
    )
    if any(
        reserva['estado'] == 'confirmada'
        and _fecha_hora(reserva['fecha_hora_inicio']) < _fecha_hora(nueva_reserva['fecha_hora_fin'])
        and _fecha_hora(reserva['fecha_hora_fin']) > _fecha_hora(nueva_reserva['fecha_hora_inicio'])
        for reserva in reservas_relacionadas
    ):
        return error_respuesta(
            'La reserva se superpone con otra reserva del socio o de la cancha',
            codigo='RESERVA_SUPERPUESTA',
        ), 409

    nueva_reserva['estado'] = 'confirmada'
    nueva_reserva['precio_hora'] = cancha['precio_hora']
    nueva_reserva['precio_total'] = int(
        cancha['precio_hora'] * nueva_reserva.pop('duracion_horas')
    )
    resultado = guardar_reserva(nueva_reserva)

    return {'mensaje': 'Reserva creada', 'reserva': resultado}, 201


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
