import csv
from flask import Flask, request

app = Flask(__name__)

# --- FUNCIONES AUXILIARES ---
def leer_canchas_desde_csv():
    canchas_db = []
    with open('canchas.csv', mode='r', encoding='utf-8') as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            # Transformamos los textos a los tipos de datos correctos
            fila['id'] = int(fila['id'])
            fila['nombre'] = fila['nombre']
            fila['id_deporte'] = int(fila['id_deporte'])
            fila['precio_hora'] = int(fila['precio_hora'])
            fila['techada'] = True if fila['techada'] == 'True' else False
            fila['activa'] = True if fila['activa'] == 'True' else False 
            
            canchas_db.append(fila)
    return canchas_db

# --- ENDPOINTS (Las rutas del API) ---

@app.route('/deportes', methods=['GET'])
def obtener_deportes():
    # El Swagger pide que los deportes sean diccionarios con id y nombre
    deportes = [
        {"id": 1, "nombre": "Futbol"},
        {"id": 2, "nombre": "Tenis"},
        {"id": 3, "nombre": "Padel"}
    ]
    return {"deportes": deportes}, 200

@app.route('/canchas', methods=['GET'])
def listar_canchas():
    # 1. Leemos el archivo CSV
    resultados = leer_canchas_desde_csv()

    # 2. Atrapamos los filtros de la URL
    filtro_nombre = request.args.get('nombre')
    filtro_techada = request.args.get('techada')
    
    # Atrapamos los datos de paginación
    limite = int(request.args.get('_limit', 10))
    offset = int(request.args.get('_offset', 0))

    # 3. Aplicamos el filtro de Nombre
    if filtro_nombre != None:
        canchas_filtradas = []
        for cancha in resultados:
            if filtro_nombre.lower() in cancha['nombre'].lower():
                canchas_filtradas.append(cancha)
        resultados = canchas_filtradas

    # 4. Aplicamos el filtro de Techada
    if filtro_techada != None:
        canchas_filtradas = []
        es_techada = True if filtro_techada == 'true' else False
        for cancha in resultados:
            if cancha['techada'] == es_techada:
                canchas_filtradas.append(cancha)
        resultados = canchas_filtradas

    # 5. Aplicamos la Paginación
    resultados_paginados = resultados[offset : offset + limite]

    # 6. Devolvemos el resultado al cliente
    return {"canchas": resultados_paginados}, 200

@app.route('/canchas', methods=['POST'])
def crear_cancha():
    # 1. Atrapar el paquete JSON que viene de Thunder Client
    # request.get_json() transforma el texto JSON, que viene en el body, en un diccionario de Python automático.
    datos = request.get_json()

    # Si el frontend mandó la petición vacía (sin cuerpo), la consigna pide rechazarlo
    if not datos:
        return {"error": "El cuerpo de la solicitud no puede estar vacío"}, 400

    # 2. CUMPLIR EL CONTRATO: Validar que existan los 3 campos obligatorios
    if 'nombre' not in datos or 'id_deporte' not in datos or 'precio_hora' not in datos:
        return {"error": "Faltan campos obligatorios: nombre, id_deporte o precio_hora"}, 400

    # 3. CUMPLIR LAS REGLAS: Validar los valores ingresados y manejar errores
    # Forzamos el nombre a string por si mandaron un número como nombre, y limpiamos espacios
    nombre_limpio = str(datos['nombre']).strip()
    precio = datos['precio_hora']

    # Manejo de error: ¿Es un número entero?
    if not isinstance(precio, int):
        return {"error": "El campo precio_hora debe ser un número entero"}, 400

    # Si pasamos la barrera anterior, sabemos con seguridad que es un int y podemos comparar
    if nombre_limpio == "" or precio <= 0:
        return {"error": "El nombre no puede estar vacío y el precio debe ser mayor a cero"}, 400

    # 4. ARMAR LA CANCHA NUEVA
    # Primero, leemos las canchas que ya existen para saber qué ID ponerle a la nueva
    canchas_existentes = leer_canchas_desde_csv()
    
    # Buscamos el ID más alto que exista y le sumamos 1
    # (Si la lista está vacía, le ponemos ID 1)
    if len(canchas_existentes) > 0:
        nuevo_id = canchas_existentes[-1]['id'] + 1
    else:
        nuevo_id = 1

    # Armamos el diccionario final aplicando los valores por defecto del contrato
    # El método .get() de los diccionarios intenta buscar la clave; si no existe, pone el valor por defecto que le digamos.
    nueva_cancha = {
        "id": nuevo_id,
        "nombre": nombre_limpio,
        "id_deporte": datos['id_deporte'],
        "precio_hora": precio,
        "techada": datos.get('techada', False), # Default false como pide el YAML
        "activa": datos.get('activa', True)     # Default true como pide el YAML
    }

    # 5. GUARDAR EN EL ARCHIVO CSV
    # Abrimos el archivo en modo 'a' (append) para agregar una línea al final sin borrar lo anterior
    with open('canchas.csv', mode='a', encoding='utf-8', newline='') as archivo:
        # Definimos el orden de las columnas tal como están en tu archivo
        columnas = ['id', 'nombre', 'id_deporte', 'precio_hora', 'techada', 'activa']
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        
        # Le decimos a Python que escriba este diccionario como una línea separada por comas
        escritor.writerow(nueva_cancha)

    # 6. RESPUESTA FINAL
    # El contrato exige devolver un 201 en lugar de un 200 cuando se crea algo exitosamente
    return {"mensaje": "Cancha creada con éxito", "cancha": nueva_cancha}, 201


# --- ARRANQUE DEL SERVIDOR ---
if __name__ == '__main__':
    app.run(debug=True)