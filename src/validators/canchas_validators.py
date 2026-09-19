from src.repositories.deportes_repositories import existe_deporte

CAMPOS_OBLIGATORIOS = ['nombre', 'id_deporte', 'precio_hora']


def validar_campos_obligatorios(datos):
    errores = []
    for campo in CAMPOS_OBLIGATORIOS:
        if campo not in datos:
            errores.append({
                "mensaje": f"Falta el campo obligatorio '{campo}'",
                "status": 400,
            })
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
        errores.append({
            "mensaje": "El campo 'nombre' no puede estar vacío o ser solo espacios",
            "status": 400,
        })

    if not isinstance(id_deporte, int):
        errores.append({
            "mensaje": "El campo 'id_deporte' debe ser un entero",
            "status": 400,
        })
    elif not existe_deporte(id_deporte):
        errores.append({
            "mensaje": f"No existe un deporte con id {id_deporte}",
            "status": 404,
        })

    if not isinstance(precio, int):
        errores.append({
            "mensaje": "El campo 'precio_hora' debe ser un entero",
            "status": 400,
        })
    elif precio <= 0:
        errores.append({
            "mensaje": "El campo 'precio_hora' debe ser mayor a cero",
            "status": 400,
        })

    if not isinstance(techada, bool):
        errores.append({
            "mensaje": "El campo 'techada' debe ser un booleano",
            "status": 400,
        })

    if not isinstance(activa, bool):
        errores.append({
            "mensaje": "El campo 'activa' debe ser un booleano",
            "status": 400,
        })

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