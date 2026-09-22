import re

from src.errores import crear_error


EMAIL_VALIDO = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
CAMPOS_EDITABLES = {'nombre', 'email', 'activo'}


def validar_filtros_socios(parametros):
    errores = []
    filtros = {}

    if parametros.get('nombre') is not None:
        filtros['nombre'] = parametros['nombre']

    activo = parametros.get('activo')
    if activo is not None:
        if activo.lower() not in ('true', 'false'):
            errores.append(
                crear_error(
                    "El parámetro 'activo' debe ser true o false",
                    codigo='ACTIVO_INVALIDO',
                    incluir_status=True,
                )
            )
        else:
            filtros['activo'] = activo.lower() == 'true'

    if errores:
        return errores, None
    return None, filtros


def validar_nuevo_socio(datos, permitir_activo=False):
    errores = []
    campos_permitidos = {'nombre', 'email'}
    if permitir_activo:
        campos_permitidos.add('activo')
    campos_desconocidos = set(datos) - campos_permitidos
    if campos_desconocidos:
        errores.append(
            crear_error(
                f"Campos desconocidos: {', '.join(sorted(campos_desconocidos))}",
                codigo='CAMPO_DESCONOCIDO',
                incluir_status=True,
            )
        )

    for campo in ('nombre', 'email'):
        if campo not in datos:
            errores.append(
                crear_error(
                    f"Falta el campo obligatorio '{campo}'",
                    codigo="CAMPO_OBLIGATORIO",
                    incluir_status=True,
                )
            )

    if errores:
        return errores, None

    nombre = datos['nombre']
    email = datos['email']

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

    if not isinstance(email, str):
        errores.append(
            crear_error(
                "El campo 'email' debe ser un texto",
                codigo="TIPO_INVALIDO",
                incluir_status=True,
            )
        )
    else:
        email_normalizado = email.strip().lower()
        if not EMAIL_VALIDO.fullmatch(email_normalizado):
            errores.append(
                crear_error(
                    "El campo 'email' debe tener un formato válido",
                    codigo="EMAIL_INVALIDO",
                    incluir_status=True,
                )
            )

    if errores:
        return errores, None

    return None, {
        'nombre': nombre.strip(),
        'email': email_normalizado,
        'activo': True,
    }


def validar_actualizacion_socio(datos, socio_actual):
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

    if 'activo' in datos and not isinstance(datos['activo'], bool):
        errores.append(
            crear_error(
                "El campo 'activo' debe ser un booleano",
                codigo="TIPO_INVALIDO",
                incluir_status=True,
            )
        )

    datos_completos = {
        'nombre': socio_actual['nombre'],
        'email': socio_actual['email'],
        'activo': socio_actual['activo'],
    }
    datos_completos.update({campo: datos[campo] for campo in datos if campo in CAMPOS_EDITABLES})

    errores_alta, socio_validado = validar_nuevo_socio(
        datos_completos,
        permitir_activo=True,
    )
    if errores_alta:
        errores.extend(errores_alta)

    if errores:
        return errores, None

    socio_validado['activo'] = datos_completos['activo']
    return None, socio_validado