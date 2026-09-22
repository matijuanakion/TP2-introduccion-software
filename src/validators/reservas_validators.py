import re
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from src.errores import crear_error


CAMPOS_OBLIGATORIOS = (
    'id_socio',
    'id_cancha',
    'fecha_hora_inicio',
    'fecha_hora_fin',
)
PATRON_FECHA_HORA = re.compile(
    r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}-03:00$'
)
ZONA_CLUB = timezone(timedelta(hours=-3))
HORA_APERTURA = 8
HORA_CIERRE = 23
MIN_DURACION_HORAS = 1
MAX_DURACION_HORAS = 3


def validar_intervalo(fecha, hora_inicio, hora_fin):
    errores = []
    inicio = datetime.strptime(
        f'{fecha}T{hora_inicio}-03:00',
        '%Y-%m-%dT%H:%M:%S-03:00',
    ).replace(tzinfo=ZONA_CLUB)
    fin = datetime.strptime(
        f'{fecha}T{hora_fin}-03:00',
        '%Y-%m-%dT%H:%M:%S-03:00',
    ).replace(tzinfo=ZONA_CLUB)
    duracion = (fin - inicio).total_seconds() / 3600
    ahora = datetime.now(ZONA_CLUB)

    if inicio <= ahora:
        errores.append(
            crear_error(
                "El inicio de la reserva debe ser posterior al momento actual",
                codigo='INICIO_NO_FUTURO',
                incluir_status=True,
            )
        )

    if inicio >= fin:
        errores.append(
            crear_error(
                "'fecha_hora_fin' debe ser posterior a 'fecha_hora_inicio'",
                codigo='INTERVALO_INVALIDO',
                incluir_status=True,
            )
        )
    elif duracion not in range(MIN_DURACION_HORAS, MAX_DURACION_HORAS + 1):
        errores.append(
            crear_error(
                'El intervalo debe durar entre una y tres horas completas',
                codigo='DURACION_INVALIDA',
                incluir_status=True,
            )
        )

    if inicio.hour < HORA_APERTURA or fin.hour > HORA_CIERRE:
        errores.append(
            crear_error(
                'El intervalo debe estar dentro del horario de atención de 08:00 a 23:00',
                codigo='HORARIO_INVALIDO',
                incluir_status=True,
            )
        )

    return errores


def validar_nueva_reserva(datos):
    errores = []
    campos_desconocidos = set(datos) - set(CAMPOS_OBLIGATORIOS)
    if campos_desconocidos:
        errores.append(
            crear_error(
                f"Campos desconocidos: {', '.join(sorted(campos_desconocidos))}",
                codigo='CAMPO_DESCONOCIDO',
                incluir_status=True,
            )
        )
    faltantes = [campo for campo in CAMPOS_OBLIGATORIOS if campo not in datos]

    for campo in faltantes:
        errores.append(
            crear_error(
                f"Falta el campo obligatorio '{campo}'",
                codigo='CAMPO_OBLIGATORIO',
                incluir_status=True,
            )
        )

    for campo in ('id_socio', 'id_cancha'):
        if campo not in datos:
            continue
        valor = datos[campo]
        if (
            not isinstance(valor, int)
            or isinstance(valor, bool)
            or valor <= 0
        ):
            errores.append(
                crear_error(
                    f"El campo '{campo}' debe ser un entero positivo",
                    codigo=f'{campo.upper()}_INVALIDO',
                    incluir_status=True,
                )
            )

    fechas = {}
    for campo in ('fecha_hora_inicio', 'fecha_hora_fin'):
        if campo not in datos:
            continue

        valor = datos[campo]
        if not isinstance(valor, str) or not PATRON_FECHA_HORA.fullmatch(valor):
            errores.append(
                crear_error(
                    f"El campo '{campo}' debe tener formato YYYY-MM-DDTHH:MM:SS.ffffff-03:00",
                    codigo='FECHA_HORA_INVALIDA',
                    incluir_status=True,
                )
            )
            continue

        try:
            fechas[campo] = datetime.strptime(
                valor,
                '%Y-%m-%dT%H:%M:%S.%f-03:00',
            )
            if fechas[campo].minute != 0 or fechas[campo].second != 0 or fechas[campo].microsecond != 0:
                errores.append(
                    crear_error(
                        f"El campo '{campo}' debe comenzar o terminar en una hora exacta",
                        codigo='HORARIO_INVALIDO',
                        incluir_status=True,
                    )
                )
        except ValueError:
            errores.append(
                crear_error(
                    f"El campo '{campo}' contiene una fecha u hora inválida",
                    codigo='FECHA_HORA_INVALIDA',
                    incluir_status=True,
                )
            )

    if len(fechas) == 2:
        errores.extend(
            validar_intervalo(
                fechas['fecha_hora_inicio'].strftime('%Y-%m-%d'),
                fechas['fecha_hora_inicio'].strftime('%H:%M:%S'),
                fechas['fecha_hora_fin'].strftime('%H:%M:%S'),
            )
        )

    if errores:
        return errores, None

    duracion_horas = Decimal(
        (fechas['fecha_hora_fin'] - fechas['fecha_hora_inicio']).total_seconds()
    ) / Decimal(3600)
    return None, {
        'id_socio': datos['id_socio'],
        'id_cancha': datos['id_cancha'],
        'fecha_hora_inicio': datos['fecha_hora_inicio'],
        'fecha_hora_fin': datos['fecha_hora_fin'],
        'duracion_horas': duracion_horas,
    }


def validar_estado_reserva(datos):
    if set(datos) != {'estado'}:
        return [
            crear_error(
                "El cuerpo debe contener únicamente el campo 'estado'",
                codigo='CUERPO_INVALIDO',
                incluir_status=True,
            )
        ], None

    if datos['estado'] not in ('confirmada', 'cancelada', 'finalizada'):
        return [
            crear_error(
                "El campo 'estado' debe ser confirmada, cancelada o finalizada",
                codigo='ESTADO_INVALIDO',
                incluir_status=True,
            )
        ], None

    return None, datos['estado']


def validar_filtros_reservas(parametros):
    errores = []
    filtros = {}

    for campo in ('id_cancha', 'id_socio'):
        valor = parametros.get(campo)
        if valor is None:
            continue
        if not valor.isascii() or not valor.isdecimal() or int(valor) <= 0:
            errores.append(
                crear_error(
                    f"El parámetro '{campo}' debe ser un entero positivo",
                    codigo=f'{campo.upper()}_INVALIDO',
                    incluir_status=True,
                )
            )
        else:
            filtros[campo] = int(valor)

    estado = parametros.get('estado')
    if estado is not None:
        if estado not in ('confirmada', 'cancelada', 'finalizada'):
            errores.append(
                crear_error(
                    "El parámetro 'estado' debe ser confirmada, cancelada o finalizada",
                    codigo='ESTADO_INVALIDO',
                    incluir_status=True,
                )
            )
        else:
            filtros['estado'] = estado

    fechas = {}
    for campo in ('fecha_desde', 'fecha_hasta'):
        valor = parametros.get(campo)
        if valor is None:
            continue
        try:
            datetime.strptime(valor, '%Y-%m-%d')
        except ValueError:
            errores.append(
                crear_error(
                    f"El parámetro '{campo}' debe tener formato YYYY-MM-DD",
                    codigo='FECHA_INVALIDA',
                    incluir_status=True,
                )
            )
        else:
            fechas[campo] = valor

    if (
        fechas.get('fecha_desde') is not None
        and fechas.get('fecha_hasta') is not None
        and fechas['fecha_desde'] > fechas['fecha_hasta']
    ):
        errores.append(
            crear_error(
                "'fecha_desde' debe ser menor o igual que 'fecha_hasta'",
                codigo='RANGO_FECHAS_INVALIDO',
                incluir_status=True,
            )
        )

    filtros.update(fechas)
    if errores:
        return errores, None
    return None, filtros