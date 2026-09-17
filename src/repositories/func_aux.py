import csv

def obtener_todas_las_canchas():
    canchas = []
    # Fijate que la ruta ahora tiene que apuntar a la carpeta database
    with open('database/canchas.csv', mode='r', encoding='utf-8') as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            # Transformamos los textos del CSV a los tipos de datos reales
            fila['id'] = int(fila['id'])
            fila['id_deporte'] = int(fila['id_deporte'])
            fila['precio_hora'] = int(fila['precio_hora'])
            # Convertimos los strings 'True'/'False' a booleanos reales de Python
            fila['techada'] = fila['techada'].lower() == 'true'
            fila['activa'] = fila['activa'].lower() == 'true'
            
            canchas.append(fila)
            
    return canchas

# Agrega la línea al CSV
def guardar_cancha(nueva_cancha):
    with open('database/canchas.csv', mode='a', encoding='utf-8', newline='') as archivo:
        columnas = ['id', 'nombre', 'id_deporte', 'precio_hora', 'techada', 'activa']
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writerow(nueva_cancha)