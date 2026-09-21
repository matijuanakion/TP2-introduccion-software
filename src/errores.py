def crear_error(mensaje, codigo='ERROR_VALIDACION', nivel='error', descripcion=None, status=400, incluir_status=False):
    detalle = {
        "code": codigo,
        "message": mensaje,
        "level": nivel,
        "description": descripcion if descripcion is not None else mensaje,
    }

    if incluir_status:
        detalle["status"] = status

    return detalle


def error_respuesta(mensaje, codigo='ERROR_VALIDACION', nivel='error', descripcion=None):
    return {
        "errors": [
            crear_error(mensaje, codigo=codigo, nivel=nivel, descripcion=descripcion)
        ]
    }