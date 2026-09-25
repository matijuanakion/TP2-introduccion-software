from datetime import datetime

from src.errores import crear_error
from src.validators.reservas_validators import validar_intervalo
from src.repositories.deportes_repositories import existe_deporte

CAMPOS_OBLIGATORIOS = ['nombre', 'id_deporte', 'precio_hora']
CAMPOS_EDITABLES = {'nombre', 'precio_hora', 'techada', 'activa'}


def validar_filtros_canchas(parametros):
    errores = []
    filtros = {}

    id_deporte = parametros.get('id_deporte')
    if id_deporte is not None:
        if not id_deporte.isascii() or not id_deporte.isdecimal() or int(id_deporte) <= 0:
            errores.append(
                crear_error(
                    "El parámetro 'id_deporte' debe ser un entero positivo",
                    codigo='ID_DEPORTE_INVALIDO',
                    incluir_status=True,
                )
            )
        else:
            filtros['id_deporte'] = int(id_deporte)

    if parametros.get('nombre') is not None:
        filtros['nombre'] = parametros['nombre']

    for campo in ('techada', 'activa'):
        valor = parametros.get(campo)
        if valor is None:
            continue
        if valor.lower() not in ('true', 'false'):
            errores.append(
                crear_error(
                    f"El parámetro '{campo}' debe ser true o false",
                    codigo=f'{campo.upper()}_INVALIDA',
                    incluir_status=True,
                )
            )
        else:
            filtros[campo] = valor.lower() == 'true'

    if errores:
        return errores, None
    return None, filtros


def validar_filtros_canchas_disponibles(parametros):
    errores = []
    filtros = {}

    for campo in ('fecha', 'hora_inicio', 'hora_fin'):
        if not parametros.get(campo):
            errores.append(
                crear_error(
                    f"El parámetro '{campo}' es obligatorio",
                    codigo='PARAMETRO_OBLIGATORIO',
                    incluir_status=True,
                )
            )

    fecha = parametros.get('fecha')
    fecha_valida = False
    if fecha:
        try:
            datetime.strptime(fecha, '%Y-%m-%d')
            fecha_valida = True
        except ValueError:
            errores.append(
                crear_error(
                    "El parámetro 'fecha' debe tener formato YYYY-MM-DD",
                    codigo='FECHA_INVALIDA',
                    incluir_status=True,
                )
            )

    horas = {}
    for campo in ('hora_inicio', 'hora_fin'):
        valor = parametros.get(campo)
        if not valor:
            continue
        try:
            horas[campo] = datetime.strptime(valor, '%H:%M:%S')
        except ValueError:
            errores.append(
                crear_error(
                    "Los parámetros 'hora_inicio' y 'hora_fin' deben tener formato HH:00:00",
                    codigo='HORARIO_INVALIDO',
                    incluir_status=True,
                )
            )
            continue
        if len(valor) != 8 or valor[2:] != ':00:00':
            errores.append(
                crear_error(
                    "Los horarios deben comenzar exactamente en una hora",
                    codigo='HORARIO_INVALIDO',
                    incluir_status=True,
                )
            )

    if fecha_valida and len(horas) == 2:
        errores.extend(
            validar_intervalo(
                fecha,
                horas['hora_inicio'].strftime('%H:%M:%S'),
                horas['hora_fin'].strftime('%H:%M:%S'),
            )
        )

    id_deporte = parametros.get('id_deporte')
    if id_deporte is not None:
        if not id_deporte.isdigit() or int(id_deporte) <= 0:
            errores.append(
                crear_error(
                    "El parámetro 'id_deporte' debe ser un entero positivo",
                    codigo='ID_DEPORTE_INVALIDO',
                    incluir_status=True,
                )
            )
        else:
            filtros['id_deporte'] = int(id_deporte)

    techada = parametros.get('techada')
    if techada is not None:
        if techada.lower() not in ('true', 'false'):
            errores.append(
                crear_error(
                    "El parámetro 'techada' debe ser true o false",
                    codigo='TECHADA_INVALIDA',
                    incluir_status=True,
                )
            )
        else:
            filtros['techada'] = techada.lower() == 'true'

    if errores:
        return errores, None

    filtros.update({
        'fecha': fecha,
        'hora_inicio': parametros['hora_inicio'],
        'hora_fin': parametros['hora_fin'],
    })
    return None, filtros


def validar_campos_obligatorios(datos):
    errores = []
    for campo in CAMPOS_OBLIGATORIOS:
        if campo not in datos:
            errores.append(
                crear_error(
                    f"Falta el campo obligatorio '{campo}'",
                    codigo="CAMPO_OBLIGATORIO",
                    incluir_status=True,
                )
            )
    return errores


def validar_nueva_cancha(datos):
    errores = validar_campos_obligatorios(datos)
    campos_permitidos = set(CAMPOS_OBLIGATORIOS) | {'techada', 'activa'}
    campos_desconocidos = set(datos) - campos_permitidos
    if campos_desconocidos:
        errores.append(
            crear_error(
                f"Campos desconocidos: {', '.join(sorted(campos_desconocidos))}",
                codigo='CAMPO_DESCONOCIDO',
                incluir_status=True,
            )
        )

    if errores:
        return errores, None

    nombre = datos['nombre']
    id_deporte = datos['id_deporte']
    precio = datos['precio_hora']
    techada = datos.get('techada', False)
    activa = datos.get('activa', True)

    if not isinstance(nombre, str):
        errores.append(
            crear_error(
                "El campo 'nombre' debe ser un texto",
                codigo="TIPO_INVALIDO",
                incluir_status=True,
            )
        )
    elif not nombre.strip():
        errores.append(
            crear_error(
                "El campo 'nombre' no puede estar vacío o ser solo espacios",
                codigo="NOMBRE_VACIO",
                incluir_status=True,
            )
        )

    if not isinstance(id_deporte, int) or isinstance(id_deporte, bool):
        errores.append(
            crear_error(
                "El campo 'id_deporte' debe ser un entero",
                codigo="TIPO_INVALIDO",
                incluir_status=True,
            )
        )
    elif not existe_deporte(id_deporte):
        errores.append(
            crear_error(
                f"No existe un deporte con id {id_deporte}",
                codigo="DEPORTE_INEXISTENTE",
                status=404,
                incluir_status=True,
            )
        )

    if not isinstance(precio, int) or isinstance(precio, bool):
        errores.append(
            crear_error(
                "El campo 'precio_hora' debe ser un entero",
                codigo="PRECIO_INVALIDO",
                incluir_status=True,
            )
        )
    elif precio <= 0:
        errores.append(
            crear_error(
                "El campo 'precio_hora' debe ser mayor a cero",
                codigo="PRECIO_INVALIDO",
                incluir_status=True,
            )
        )

    if not isinstance(techada, bool):
        errores.append(
            crear_error(
                "El campo 'techada' debe ser un booleano",
                codigo="TIPO_INVALIDO",
                incluir_status=True,
            )
        )

    if not isinstance(activa, bool):
        errores.append(
            crear_error(
                "El campo 'activa' debe ser un booleano",
                codigo="TIPO_INVALIDO",
                incluir_status=True,
            )
        )

    if errores:
        return errores, None

    cancha = {
        "nombre": nombre.strip(),
        "id_deporte": id_deporte,
        "precio_hora": precio,
        "techada": techada,
        "activa": activa,
    }
    return None, cancha


def validar_actualizacion_cancha(datos, cancha_actual):
    errores = []

    campos_no_editables = set(datos) - CAMPOS_EDITABLES
    if campos_no_editables:
        errores.append(
            crear_error(
                f"Campos no editables: {', '.join(sorted(campos_no_editables))}",
                codigo="CAMPO_NO_EDITABLE",
                incluir_status=True,
            )
        )

    if not datos:
        errores.append(
            crear_error(
                "Debe indicarse al menos un campo editable",
                codigo="CUERPO_VACIO",
                incluir_status=True,
            )
        )

    datos_completos = {
        'nombre': cancha_actual['nombre'],
        'id_deporte': cancha_actual['id_deporte'],
        'precio_hora': cancha_actual['precio_hora'],
        'techada': cancha_actual['techada'],
        'activa': cancha_actual['activa'],
    }
    datos_completos.update({campo: datos[campo] for campo in datos if campo in CAMPOS_EDITABLES})

    errores_alta, cancha_validada = validar_nueva_cancha(datos_completos)
    if errores_alta:
        errores.extend(errores_alta)

    if errores:
        return errores, None

    return None, cancha_validada