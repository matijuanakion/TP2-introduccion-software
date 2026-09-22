from flask import Blueprint, request

from src.errores import error_respuesta
from src.services.socios_services import (
    consultar_socio,
    filtrar_socios,
    procesar_nuevo_socio,
    procesar_actualizacion_socio,
)
from src.utils import (
    armar_links,
    obtener_datos_json,
    obtener_paginacion,
    respuesta_validacion,
    validar_id,
    validar_parametros,
)
from src.validators.socios_validators import validar_filtros_socios

socios_bp = Blueprint('socios_bp', __name__)


@socios_bp.route('/socios/<id_socio>', methods=['GET'])
def obtener_socio(id_socio):
    try:
        error = validar_parametros()

        if error:
            return error

        id_numerico, error, status_code = validar_id(id_socio)
        if error:
            return error, status_code

        respuesta, status_code = consultar_socio(id_numerico)
        return respuesta, status_code
    except Exception as exc:
        return error_respuesta(
            "Error interno del servidor",
            codigo="ERROR_INTERNO",
        ), 500


@socios_bp.route('/socios/<id_socio>', methods=['PATCH'])
def actualizar_socio_por_id(id_socio):
    try:
        error = validar_parametros()

        if error:
            return error

        id_numerico, error, status_code = validar_id(id_socio)
        if error:
            return error, status_code

        datos, error, status_code = obtener_datos_json()
        if error:
            return error, status_code

        return procesar_actualizacion_socio(id_numerico, datos)
    except Exception as exc:
        return error_respuesta(
            "Error interno del servidor",
            codigo="ERROR_INTERNO",
        ), 500


@socios_bp.route('/socios', methods=['POST'])
def crear_socio():
    try:
        datos, error, status_code = obtener_datos_json()
        if error:
            return error, status_code

        respuesta, status_code = procesar_nuevo_socio(datos)
        return respuesta, status_code
    except Exception as exc:
        return error_respuesta(
            "Error interno del servidor",
            codigo="ERROR_INTERNO",
        ), 500


@socios_bp.route('/socios', methods=['GET'])
def listar_socios():
    try:
        error = validar_parametros({'nombre', 'activo', '_limit', '_offset'})
        if error:
            return error

        errores, filtros = validar_filtros_socios(request.args)
        if errores:
            return respuesta_validacion(errores)

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
        ), 500