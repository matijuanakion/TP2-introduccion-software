from datetime import datetime, timedelta, timezone

from src.errores import crear_error


ZONA_CLUB = timezone(timedelta(hours=-3))
HORA_APERTURA = 8
HORA_CIERRE = 23
CAMPOS_BLOQUEO = {'id_cancha', 'fecha', 'hora_inicio', 'hora_fin', 'motivo'}


def validar_bloqueo(datos):
    errores = []
    desconocidos = set(datos) - CAMPOS_BLOQUEO
    if desconocidos:
        errores.append(crear_error(
            f"Campos desconocidos: {', '.join(sorted(desconocidos))}",
            codigo='CAMPO_DESCONOCIDO', incluir_status=True,
        ))

    for campo in CAMPOS_BLOQUEO - set(datos):
        errores.append(crear_error(
            f"Falta el campo obligatorio '{campo}'",
            codigo='CAMPO_OBLIGATORIO', incluir_status=True,
        ))

    id_cancha = datos.get('id_cancha')
    if not isinstance(id_cancha, int) or isinstance(id_cancha, bool) or id_cancha <= 0:
        errores.append(crear_error(
            "El campo 'id_cancha' debe ser un entero positivo",
            codigo='ID_CANCHA_INVALIDO', incluir_status=True,
        ))

    fecha = datos.get('fecha')
    hora_inicio = datos.get('hora_inicio')
    hora_fin = datos.get('hora_fin')
    motivo = datos.get('motivo')
    formato_hora = '%H:%M:%S'
    inicio = fin = None

    try:
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        fecha_obj = None
        errores.append(crear_error(
            "El campo 'fecha' debe tener formato YYYY-MM-DD",
            codigo='FECHA_INVALIDA', incluir_status=True,
        ))

    try:
        inicio = datetime.strptime(hora_inicio, formato_hora).time()
        fin = datetime.strptime(hora_fin, formato_hora).time()
        if inicio.minute or inicio.second or fin.minute or fin.second:
            raise ValueError
    except (TypeError, ValueError):
        errores.append(crear_error(
            "'hora_inicio' y 'hora_fin' deben tener formato HH:MM:SS en horas exactas",
            codigo='HORARIO_INVALIDO', incluir_status=True,
        ))

    if not isinstance(motivo, str) or not motivo.strip():
        errores.append(crear_error(
            "El campo 'motivo' debe ser un texto no vacío",
            codigo='MOTIVO_INVALIDO', incluir_status=True,
        ))
    elif len(motivo) > 255:
        errores.append(crear_error(
            "El campo 'motivo' no puede superar los 255 caracteres",
            codigo='MOTIVO_INVALIDO', incluir_status=True,
        ))

    if fecha_obj is not None and inicio is not None and fin is not None:
        comienzo = datetime.combine(fecha_obj, inicio, tzinfo=ZONA_CLUB)
        ahora = datetime.now(ZONA_CLUB)
        if comienzo <= ahora:
            errores.append(crear_error(
                'El inicio del bloqueo debe ser posterior al momento actual',
                codigo='INICIO_NO_FUTURO', incluir_status=True,
            ))
        if inicio >= fin:
            errores.append(crear_error(
                "'hora_fin' debe ser posterior a 'hora_inicio'",
                codigo='INTERVALO_INVALIDO', incluir_status=True,
            ))
        if inicio.hour < HORA_APERTURA or fin.hour > HORA_CIERRE:
            errores.append(crear_error(
                'El bloqueo debe estar dentro del horario de atención de 08:00 a 23:00',
                codigo='HORARIO_INVALIDO', incluir_status=True,
            ))

    if errores:
        return errores, None
    return None, {
        'id_cancha': id_cancha,
        'fecha': fecha,
        'hora_inicio': hora_inicio,
        'hora_fin': hora_fin,
        'motivo': motivo.strip(),
    }


def validar_filtros_bloqueos(parametros):
    errores = []
    filtros = {}
    id_cancha = parametros.get('id_cancha')
    if id_cancha is not None:
        if not id_cancha.isascii() or not id_cancha.isdecimal() or int(id_cancha) <= 0:
            errores.append(crear_error(
                "El parámetro 'id_cancha' debe ser un entero positivo",
                codigo='ID_CANCHA_INVALIDO', incluir_status=True,
            ))
        else:
            filtros['id_cancha'] = int(id_cancha)

    fecha = parametros.get('fecha')
    if fecha is not None:
        try:
            datetime.strptime(fecha, '%Y-%m-%d')
        except ValueError:
            errores.append(crear_error(
                "El parámetro 'fecha' debe tener formato YYYY-MM-DD",
                codigo='FECHA_INVALIDA', incluir_status=True,
            ))
        else:
            filtros['fecha'] = fecha
    return errores, filtros
