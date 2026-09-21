from src.errores import error_respuesta
from src.repositories.canchas_repositories import (
    obtener_cancha_por_id,
    obtener_canchas_paginadas,
    contar_canchas,
    guardar_cancha,
)
from src.validators.canchas_validators import validar_nueva_cancha


def filtrar_canchas(filtros, limit, offset):
    canchas = obtener_canchas_paginadas(filtros, limit, offset)
    total = contar_canchas(filtros)
    return canchas, total


def procesar_nueva_cancha(datos):
    errores, nueva_cancha = validar_nueva_cancha(datos)

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

    cancha_guardada = guardar_cancha(nueva_cancha)

    return {"mensaje": "Cancha creada", "cancha": cancha_guardada}, 201


def consultar_cancha(id_cancha):
    cancha = obtener_cancha_por_id(id_cancha)

    if cancha is None:
        return error_respuesta(
            f"No existe una cancha con id {id_cancha}",
            codigo="CANCHA_INEXISTENTE",
        ), 404

    return cancha, 200