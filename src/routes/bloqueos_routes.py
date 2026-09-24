from flask import Blueprint, request

from src.errores import error_respuesta
from src.services.bloqueos_services import (
    filtrar_bloqueos,
    procesar_eliminacion_bloqueo,
    procesar_nuevo_bloqueo,
)
from src.utils import (
    armar_links,
    obtener_datos_json,
    obtener_paginacion,
    respuesta_validacion,
    validar_id,
    validar_parametros,
)
from src.validators.bloqueos_validators import validar_filtros_bloqueos

bloqueos_bp = Blueprint('bloqueos_bp', __name__)


@bloqueos_bp.route('/bloqueos', methods=['GET'])
def listar_bloqueos():
    try:
        error = validar_parametros({'id_cancha', 'fecha', '_limit', '_offset'})
        if error:
            return error
        errores, filtros = validar_filtros_bloqueos(request.args)
        if errores:
            return respuesta_validacion(errores)
        limit, offset, error, status_code = obtener_paginacion()
        if error:
            return error, status_code
        bloqueos, total = filtrar_bloqueos(filtros, limit, offset)
        if not bloqueos:
            return '', 204
        base_url = request.host_url.rstrip('/') + request.path
        return {'bloqueos': bloqueos, '_links': armar_links(base_url, filtros, limit, offset, total)}, 200
    except Exception:
        return error_respuesta('Error interno del servidor', codigo='ERROR_INTERNO'), 500


@bloqueos_bp.route('/bloqueos', methods=['POST'])
def crear_bloqueo():
    try:
        datos, error, status_code = obtener_datos_json()
        if error:
            return error, status_code
        return procesar_nuevo_bloqueo(datos)
    except Exception:
        return error_respuesta('Error interno del servidor', codigo='ERROR_INTERNO'), 500


@bloqueos_bp.route('/bloqueos/<id_bloqueo>', methods=['DELETE'])
def eliminar_bloqueo_por_id(id_bloqueo):
    try:
        error = validar_parametros()
        if error:
            return error
        id_numerico, error, status_code = validar_id(id_bloqueo)
        if error:
            return error, status_code
        return procesar_eliminacion_bloqueo(id_numerico)
    except Exception:
        return error_respuesta('Error interno del servidor', codigo='ERROR_INTERNO'), 500
