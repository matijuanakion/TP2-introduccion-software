from flask import Blueprint, request

from src.errores import error_respuesta
from src.services.socios_services import filtrar_socios
from src.utils import armar_links, obtener_paginacion, validar_parametros

socios_bp = Blueprint('socios_bp', __name__)


@socios_bp.route('/socios', methods=['GET'])
def listar_socios():
    try:
        error = validar_parametros({'nombre', 'activo', '_limit', '_offset'})
        if error:
            return error

        filtros = {}

        nombre = request.args.get('nombre')
        if nombre is not None:
            filtros['nombre'] = nombre

        activo = request.args.get('activo')
        if activo is not None:
            if activo.lower() not in ('true', 'false'):
                return error_respuesta(
                    "El parámetro 'activo' debe ser true o false"
                ), 400
            filtros['activo'] = activo.lower() == 'true'

        limit, offset, error, status_code = obtener_paginacion()
        if error:
            return error, status_code

        socios, total = filtrar_socios(filtros, limit, offset)
        base_url = request.host_url.rstrip('/') + request.path
        links = armar_links(base_url, filtros, limit, offset, total)

        if len(socios) == 0:
            return "", 204

        return {"socios": socios, "_links": links}, 200
    except Exception as exc:
        return error_respuesta(
            "Error interno del servidor",
            codigo="ERROR_INTERNO",
            descripcion=str(exc),
        ), 500