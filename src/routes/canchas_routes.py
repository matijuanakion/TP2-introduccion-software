from flask import Blueprint, request

from src.errores import error_respuesta

from src.services.canchas_services import (
    consultar_cancha,
    filtrar_canchas,
    filtrar_canchas_disponibles,
    procesar_actualizacion_cancha,
    procesar_eliminacion_cancha,
    procesar_nueva_cancha,
)

from src.utils import (
    armar_links,
    obtener_datos_json,
    obtener_paginacion,
    respuesta_validacion,
    validar_id,
    validar_parametros,
)
from src.validators.canchas_validators import (
    validar_filtros_canchas,
    validar_filtros_canchas_disponibles,
)

canchas_bp = Blueprint('canchas_bp', __name__)


@canchas_bp.route('/canchas/disponibles', methods=['GET'])
def listar_canchas_disponibles():
    try:
        error = validar_parametros({
            'fecha',
            'hora_inicio',
            'hora_fin',
            'id_deporte',
            'techada',
            '_limit',
            '_offset',
        })
        if error:
            return error

        errores, filtros = validar_filtros_canchas_disponibles(request.args)
        if errores:
            return respuesta_validacion(errores)

        limit, offset, error, status_code = obtener_paginacion()
        if error:
            return error, status_code

        canchas, total = filtrar_canchas_disponibles(filtros, limit, offset)
        base_url = request.host_url.rstrip('/') + request.path
        links = armar_links(base_url, filtros, limit, offset, total)

        return {"canchas": canchas, "_links": links}, 200
    except Exception as exc:
        return error_respuesta(
            "Error interno del servidor",
            codigo="ERROR_INTERNO",
            descripcion=str(exc),
        ), 500

@canchas_bp.route('/canchas', methods=['GET'])
def listar_canchas():
    try:
        error = validar_parametros({
            'id_deporte',
            'nombre',
            'techada',
            'activa',
            '_limit',
            '_offset',
        })

        if error:
            return error

        errores, filtros = validar_filtros_canchas(request.args)
        if errores:
            return respuesta_validacion(errores)

        limit, offset, error, status_code = obtener_paginacion()
        if error:
            return error, status_code

        canchas, total = filtrar_canchas(filtros, limit, offset)

        base_url = request.host_url.rstrip('/') + request.path
        links = armar_links(base_url, filtros, limit, offset, total)

        if len(canchas) == 0:
            return "", 204

        return {"canchas": canchas, "_links": links}, 200
    except Exception as exc:
        return error_respuesta(
            "Error interno del servidor",
            codigo="ERROR_INTERNO",
            descripcion=str(exc),
        ), 500


@canchas_bp.route('/canchas', methods=['POST'])
def crear_cancha():
    try:
        datos, error, status_code = obtener_datos_json()
        if error:
            return error, status_code

        respuesta, status_code = procesar_nueva_cancha(datos)
        return respuesta, status_code
    except Exception as exc:
        return error_respuesta(
            "Error interno del servidor",
            codigo="ERROR_INTERNO",
            descripcion=str(exc),
        ), 500


@canchas_bp.route('/canchas/<id_cancha>', methods=['GET'])
def obtener_cancha(id_cancha):
    try:
        error = validar_parametros()

        if error:
            return error

        id_numerico, error, status_code = validar_id(id_cancha)
        if error:
            return error, status_code

        respuesta, status_code = consultar_cancha(id_numerico)

        return respuesta, status_code
    except Exception as exc:
        return error_respuesta(
            "Error interno del servidor",
            codigo="ERROR_INTERNO",
            descripcion=str(exc),
        ), 500


@canchas_bp.route('/canchas/<id_cancha>', methods=['PATCH'])
def actualizar_cancha_por_id(id_cancha):
    try:
        error = validar_parametros()

        if error:
            return error

        id_numerico, error, status_code = validar_id(id_cancha)
        if error:
            return error, status_code

        datos, error, status_code = obtener_datos_json()
        if error:
            return error, status_code

        return procesar_actualizacion_cancha(id_numerico, datos)
    except Exception as exc:
        return error_respuesta(
            "Error interno del servidor",
            codigo="ERROR_INTERNO",
            descripcion=str(exc),
        ), 500


@canchas_bp.route('/canchas/<id_cancha>', methods=['DELETE'])
def eliminar_cancha_por_id(id_cancha):
    try:
        error = validar_parametros()

        if error:
            return error

        id_numerico, error, status_code = validar_id(id_cancha)
        if error:
            return error, status_code

        return procesar_eliminacion_cancha(id_numerico)
    except Exception as exc:
        return error_respuesta(
            "Error interno del servidor",
            codigo="ERROR_INTERNO",
            descripcion=str(exc),
        ), 500