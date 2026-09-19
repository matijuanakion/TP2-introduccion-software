from flask import Blueprint, request

from src.errores import error_respuesta
from src.services.canchas_services import filtrar_canchas, procesar_nueva_cancha
from src.utils import armar_links

# Creamos el Blueprint. Lo llamamos 'canchas_bp' (bp por Blueprint)
canchas_bp = Blueprint('canchas_bp', __name__)


@canchas_bp.route('/canchas', methods=['GET'])
def listar_canchas():
    filtros = {}

    # Filtro por deporte
    id_deporte = request.args.get('id_deporte')
    if id_deporte is not None:
        if not id_deporte.isdigit():
            return error_respuesta("El parámetro 'id_deporte' debe ser un entero"), 400
        filtros['id_deporte'] = int(id_deporte)

    # Filtro por nombre (búsqueda parcial e insensible a mayúsculas)
    nombre = request.args.get('nombre')
    if nombre is not None:
        filtros['nombre'] = nombre

    # Filtros booleanos: techada y activa
    for campo in ('techada', 'activa'):
        valor = request.args.get(campo)
        if valor is not None:
            if valor.lower() not in ('true', 'false'):
                return error_respuesta(f"El parámetro '{campo}' debe ser true o false"), 400
            filtros[campo] = valor.lower() == 'true'

    # Paginación
    try:
        limit = int(request.args.get('_limit', 10))
        offset = int(request.args.get('_offset', 0))
    except ValueError:
        return error_respuesta("Los parámetros '_limit' y '_offset' deben ser enteros"), 400

    if limit < 1 or offset < 0:
        return error_respuesta("'_limit' debe ser mayor a 0 y '_offset' mayor o igual a 0"), 400

    # Le pasamos los parámetros a la funcion de services
    canchas, total = filtrar_canchas(filtros, limit, offset)

    if total == 0:
        return '', 204

    base_url = request.host_url.rstrip('/') + request.path
    links = armar_links(base_url, filtros, limit, offset, total)

    # Devolvemos el diccionario con la clave "canchas" que exige el contrato y el código 200
    return {"canchas": canchas, "_links": links}, 200


@canchas_bp.route('/canchas', methods=['POST'])
def crear_cancha():
    datos = request.get_json()

    if not datos:
        return error_respuesta("El cuerpo de la solicitud no puede estar vacío"), 400

    respuesta, status_code = procesar_nueva_cancha(datos)
    return respuesta, status_code