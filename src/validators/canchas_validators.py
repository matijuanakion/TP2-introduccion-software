from src.repositories.deportes_repositories import existe_deporte

CAMPOS_OBLIGATORIOS = ['nombre', 'id_deporte', 'precio_hora']


def _error(mensaje, codigo='ERROR_VALIDACION', status=400):
    return {"mensaje": mensaje, "codigo": codigo, "status": status}


def validar_campos_obligatorios(datos):
    errores = []
    for campo in CAMPOS_OBLIGATORIOS:
        if campo not in datos:
            errores.append(_error(f"Falta el campo obligatorio '{campo}'", "CAMPO_OBLIGATORIO"))
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
        errores.append(_error("El campo 'nombre' no puede estar vacío o ser solo espacios", "NOMBRE_VACIO"))

    if not isinstance(id_deporte, int):
        errores.append(_error("El campo 'id_deporte' debe ser un entero", "TIPO_INVALIDO"))
    elif not existe_deporte(id_deporte):
        errores.append(_error(f"No existe un deporte con id {id_deporte}", "DEPORTE_INEXISTENTE", 404))

    if not isinstance(precio, int):
        errores.append(_error("El campo 'precio_hora' debe ser un entero", "PRECIO_INVALIDO"))
    elif precio <= 0:
        errores.append(_error("El campo 'precio_hora' debe ser mayor a cero", "PRECIO_INVALIDO"))

    if not isinstance(techada, bool):
        errores.append(_error("El campo 'techada' debe ser un booleano", "TIPO_INVALIDO"))

    if not isinstance(activa, bool):
        errores.append(_error("El campo 'activa' debe ser un booleano", "TIPO_INVALIDO"))

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