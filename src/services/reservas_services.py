from datetime import datetime, timedelta, timezone

from src.errores import error_respuesta
from src.repositories.reservas_repositories import (
    contar_reservas,
    guardar_reserva,
    obtener_reservas_paginadas,
)
from src.validators.reservas_validators import validar_nueva_reserva


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

    resultado = guardar_reserva(nueva_reserva)
    errores = {
        'socio_inexistente': ("No existe un socio con ese id", 'SOCIO_INEXISTENTE', 404),
        'socio_inactivo': ("El socio no está activo", 'SOCIO_INACTIVO', 409),
        'cancha_inexistente': ("No existe una cancha con ese id", 'CANCHA_INEXISTENTE', 404),
        'cancha_inactiva': ("La cancha no está activa", 'CANCHA_INACTIVA', 409),
        'superposicion': (
            'La reserva se superpone con otra reserva del socio o de la cancha',
            'RESERVA_SUPERPUESTA',
            409,
        ),
    }
    if isinstance(resultado, str) and resultado in errores:
        mensaje, codigo, status_code = errores[resultado]
        return error_respuesta(mensaje, codigo=codigo), status_code

    return {'mensaje': 'Reserva creada', 'reserva': resultado}, 201
