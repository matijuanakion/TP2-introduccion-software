# Importamos las funciones de repositorio
from src.repositories.func_aux import obtener_todas_las_canchas, guardar_cancha
from src.repositories.func_aux import obtener_todas_las_canchas


def filtrar_canchas(parametro_techada, limit, offset):
    # 1. Le pedimos los datos de todas las canchas 
    todas_las_canchas = obtener_todas_las_canchas()
    canchas_filtradas = todas_las_canchas

    # 2.  Si el usuario no mandó ningún filtro en la URL, el valor default es offset 10 como pide el swagger
    # 2.5 filtra por el parametro techada o no techada de la lista de todas las canchas y eso lo manda a canchas_filtradas
    if parametro_techada is not None:
        es_techada = parametro_techada.lower() == 'true'
        canchas_filtradas = [c for c in todas_las_canchas if c['techada'] == es_techada]

    #3    hace la paginacion de 10 canchas a la vez 
    canchas_paginadas = canchas_filtradas[offset : offset + limit]
            
    return canchas_paginadas

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

    # 3. Calcular nuevo ID pidiéndole las canchas al archivero
    canchas_existentes = obtener_todas_las_canchas()
    nuevo_id = canchas_existentes[-1]['id'] + 1 if canchas_existentes else 1

    # 4. Armar el diccionario final
    nueva_cancha = {
        "id": nuevo_id,
        "nombre": nombre_limpio,
        "id_deporte": datos['id_deporte'],
        "precio_hora": precio,
        "techada": datos.get('techada', False),
        "activa": datos.get('activa', True)
    }

    # 5. Mandar a guardar al archivero
    guardar_cancha(nueva_cancha)

    # 6. Devolver éxito
    return {"mensaje": "Cancha creada", "cancha": nueva_cancha}, 201