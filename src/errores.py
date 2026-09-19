def error_respuesta(mensaje, codigo='ERROR_VALIDACION', nivel='error', descripcion=None):
    return {
        "errors": [
            {
                "code": codigo,
                "message": mensaje,
                "level": nivel,
                "description": descripcion if descripcion else mensaje,
            }
        ]
    }