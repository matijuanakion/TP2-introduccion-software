# Importamos las funciones de repositorio
from src.repositories.func_aux import obtener_canchas_paginadas, guardar_cancha
from src.validators.canchas_validators import validar_nueva_cancha


def filtrar_canchas(parametro_techada, limit, offset):
    # Simplemente le pasamos los parámetros al archivero y devolvemos lo que nos da
    return obtener_canchas_paginadas(parametro_techada, limit, offset)


def procesar_nueva_cancha(datos):
    # 1. Toda la validación de entrada la hacen los validators
    errores, nueva_cancha = validar_nueva_cancha(datos)

    if errores:
        return {"error": errores[0]['mensaje']}, errores[0]['status']

    # 2. Mandar a guardar al archivero y que nos devuelva la cancha con su ID oficial
    cancha_guardada = guardar_cancha(nueva_cancha)

    # 3. Devolver éxito
    return {"mensaje": "Cancha creada", "cancha": cancha_guardada}, 201