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

# --- ARRANQUE DEL SERVIDOR ---
if __name__ == '__main__':
    app.run(debug=True)