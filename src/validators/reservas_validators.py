import re
from datetime import datetime
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


def validar_nueva_reserva(datos):
    errores = []
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
        except ValueError:
            errores.append(
                crear_error(
                    f"El campo '{campo}' contiene una fecha u hora inválida",
                    codigo='FECHA_HORA_INVALIDA',
                    incluir_status=True,
                )
            )

    if len(fechas) == 2 and fechas['fecha_hora_fin'] <= fechas['fecha_hora_inicio']:
        errores.append(
            crear_error(
                "'fecha_hora_fin' debe ser posterior a 'fecha_hora_inicio'",
                codigo='INTERVALO_INVALIDO',
                incluir_status=True,
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