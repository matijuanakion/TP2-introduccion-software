# Importamos las funciones de repositorio
from src.repositories.func_aux import obtener_canchas_paginadas, guardar_cancha
from src.repositories.func_aux import obtener_canchas_paginadas


def filtrar_canchas(parametro_techada, limit, offset):
    # 2. Simplemente le pasamos los parámetros al archivero y devolvemos lo que nos da
    canchas = obtener_canchas_paginadas(parametro_techada, limit, offset)
    return canchas



def procesar_nueva_cancha(datos):
    # 1. Validar campos obligatorios
    if 'nombre' not in datos or 'id_deporte' not in datos or 'precio_hora' not in datos:
        return {"error": "Faltan campos obligatorios"}, 400

    # 2. Validar tipos de datos y reglas
    nombre_limpio = str(datos['nombre']).strip()
    precio = datos['precio_hora']

    if not isinstance(precio, int):
        return {"error": "El precio_hora debe ser entero"}, 400

    if nombre_limpio == "" or precio <= 0:
        return {"error": "Nombre vacío o precio inválido"}, 400

    # 3. Armar el diccionario final 
    nueva_cancha = {
        "nombre": nombre_limpio,
        "id_deporte": datos['id_deporte'],
        "precio_hora": precio,
        "techada": datos.get('techada', False),
        "activa": datos.get('activa', True)
    }

    # 4. Mandar a guardar al archivero y que nos devuelva la cancha con su ID oficial
    cancha_guardada = guardar_cancha(nueva_cancha)

    # 5. Devolver éxito
    return {"mensaje": "Cancha creada", "cancha": cancha_guardada}, 201
