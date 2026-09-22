from src.repositories.socios_repositories import (
    contar_socios,
    guardar_socio,
    obtener_socio_por_id,
    obtener_socios_paginados,
    actualizar_socio,
)
from src.errores import error_respuesta
from src.validators.socios_validators import (
    validar_nuevo_socio,
    validar_actualizacion_socio,
)


def filtrar_socios(filtros, limit, offset):
    socios = obtener_socios_paginados(filtros, limit, offset)
    total = contar_socios(filtros)
    return socios, total


def consultar_socio(id_socio):
    socio = obtener_socio_por_id(id_socio)

    if socio is None:
        return error_respuesta(
            f"No existe un socio con id {id_socio}",
            codigo="SOCIO_INEXISTENTE",
        ), 404

    return socio, 200


def procesar_nuevo_socio(datos):
    errores, nuevo_socio = validar_nuevo_socio(datos)

    if errores:
        return (
            {
                "errors": [
                    {
                        "code": error["code"],
                        "message": error["message"],
                        "level": error.get("level", "error"),
                        "description": error.get("description", error["message"]),
                    }
                    for error in errores
                ]
            },
            max((error.get("status", 400) for error in errores), default=400),
        )

    socio_guardado = guardar_socio(nuevo_socio)
    if socio_guardado is None:
        return error_respuesta(
            "Ya existe un socio registrado con ese email",
            codigo="EMAIL_DUPLICADO",
        ), 409

    return {"mensaje": "Socio creado", "socio": socio_guardado}, 201


def procesar_actualizacion_socio(id_socio, datos):
    campos_no_editables = set(datos) - {'nombre', 'email', 'activo'}
    if not datos or campos_no_editables:
        return error_respuesta(
            'Debe indicarse al menos un campo editable y no incluir campos desconocidos',
            codigo='CUERPO_INVALIDO',
        ), 400

    socio_actual = obtener_socio_por_id(id_socio)

    if socio_actual is None:
        return error_respuesta(
            f"No existe un socio con id {id_socio}",
            codigo="SOCIO_INEXISTENTE",
        ), 404

    errores, socio_actualizado = validar_actualizacion_socio(datos, socio_actual)

    if errores:
        return (
            {
                "errors": [
                    {
                        "code": error["code"],
                        "message": error["message"],
                        "level": error.get("level", "error"),
                        "description": error.get("description", error["message"]),
                    }
                    for error in errores
                ]
            },
            max((error.get("status", 400) for error in errores), default=400),
        )

    if not actualizar_socio(id_socio, socio_actualizado):
        return error_respuesta(
            "Ya existe un socio registrado con ese email",
            codigo="EMAIL_DUPLICADO",
        ), 409

    return "", 204