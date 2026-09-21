from src.errores import crear_error
from src.repositories.deportes_repositories import existe_deporte

CAMPOS_OBLIGATORIOS = ['nombre', 'id_deporte', 'precio_hora']
CAMPOS_EDITABLES = {'nombre', 'precio_hora', 'techada', 'activa'}


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

    if errores:
        return errores, None

    nombre = str(datos['nombre']).strip()
    id_deporte = datos['id_deporte']
    precio = datos['precio_hora']
    techada = datos.get('techada', False)
    activa = datos.get('activa', True)

    if nombre == "":
        errores.append(
            crear_error(
                "El campo 'nombre' no puede estar vacío o ser solo espacios",
                codigo="NOMBRE_VACIO",
                incluir_status=True,
            )
        )

    if not isinstance(id_deporte, int):
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

    if not isinstance(precio, int):
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
        "nombre": nombre,
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