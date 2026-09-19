from src.errores import error_respuesta
from src.repositories.canchas_repositories import (
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
    # 1. Toda la validación de entrada la hacen los validators
    errores, nueva_cancha = validar_nueva_cancha(datos)

    if errores:
        return error_respuesta(errores[0]['mensaje'], codigo=errores[0]['codigo']), errores[0]['status']

    # 2. Mandar a guardar al archivero y que nos devuelva la cancha con su ID oficial
    cancha_guardada = guardar_cancha(nueva_cancha)

    # 3. Devolver éxito
    return {"mensaje": "Cancha creada", "cancha": cancha_guardada}, 201