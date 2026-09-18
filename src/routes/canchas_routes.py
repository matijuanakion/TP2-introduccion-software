from flask import Blueprint, request
from src.services.canchas_services import procesar_nueva_cancha
from src.services.canchas_services import filtrar_canchas

# Creamos el Blueprint. Lo llamamos 'canchas_bp' (bp por Blueprint)
canchas_bp = Blueprint('canchas_bp', __name__)


@canchas_bp.route('/canchas', methods=['GET'])
def listar_canchas():
    
    # 1. agarra parametros de la URL 
    filtro_techada = request.args.get('techada')
    limit = request.args.get('_limit', default=10, type=int)
    offset = request.args.get('_offset', default=0, type=int)

    # 2. Le pasamos los parametros a la funcion de services
    resultados = filtrar_canchas(filtro_techada, limit, offset)
    
    # 3. Devolvemos el diccionario con la clave "canchas" que exige el contrato y el código 200
    return {"canchas": resultados}, 200



@canchas_bp.route('/canchas', methods=['POST'])
def crear_cancha():
    # 1. Agarra el body del poost
    datos = request.get_json()
    
    if not datos:
        return {"error": "Cuerpo vacío"}, 400

    # 2. se verifica con la funcion de services y devuelve su respuesta
    respuesta, status_code = procesar_nueva_cancha(datos)
    return respuesta, status_code