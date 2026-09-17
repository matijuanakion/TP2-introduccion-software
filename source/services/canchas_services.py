# Importamos las funciones de repositorio
from source.repositories.func_aux import obtener_todas_las_canchas, guardar_cancha
from source.repositories.func_aux import obtener_todas_las_canchas


def filtrar_canchas(parametro_techada):
    # 1. Le pedimos los datos de todas las canchas 
    todas_las_canchas = obtener_todas_las_canchas()
    
    # 2. Si el usuario no mandó ningún filtro en la URL, devolvemos todo tal cual
    if parametro_techada is None:
        return todas_las_canchas
        
    # 3. filtramos si mand otechada
    canchas_filtradas = []
    # Transformamos lo que vino de la URL ('true' o 'false') a un booleano de Python
    es_techada = parametro_techada.lower() == 'true'
    
    for cancha in todas_las_canchas:
        if cancha['techada'] == es_techada:
            canchas_filtradas.append(cancha)
            
    return canchas_filtradas

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