from flask import Blueprint, request

from src.errores import error_respuesta
from src.services.reservas_services import (
    consultar_reserva,
    filtrar_reservas,
    procesar_estado_reserva,
    procesar_nueva_reserva,
    procesar_reservas_recurrentes,
)
from src.utils import (
    armar_links,
    obtener_datos_json,
    obtener_paginacion,
    respuesta_validacion,
    validar_id,
    validar_parametros,
)
from src.validators.reservas_validators import (
    validar_estado_reserva,
    validar_filtros_reservas,
)


reservas_bp = Blueprint('reservas_bp', __name__)


@reservas_bp.route('/reservas/recurrentes', methods=['POST'])
def crear_reservas_recurrentes():
    try:
        datos, error, status_code = obtener_datos_json()
        if error:
            return error, status_code
        return procesar_reservas_recurrentes(datos)
    except Exception:
        return error_respuesta(
            'Error interno del servidor', codigo='ERROR_INTERNO'
        ), 500


@reservas_bp.route('/reservas', methods=['POST'])
def crear_reserva():
    try:
        datos, error, status_code = obtener_datos_json()
        if error:
            return error, status_code

        return procesar_nueva_reserva(datos)
    except Exception as exc:
        return error_respuesta(
            "Error interno del servidor",
            codigo="ERROR_INTERNO",
        ), 500


@reservas_bp.route('/reservas', methods=['GET'])
def listar_reservas():
    try:
        error = validar_parametros({
            'id_cancha',
            'id_socio',
            'estado',
            'fecha_desde',
            'fecha_hasta',
            '_limit',
            '_offset',
        })
        if error:
            return error

        errores, filtros = validar_filtros_reservas(request.args)
        if errores:
            return respuesta_validacion(errores)

        limit, offset, error, status_code = obtener_paginacion()
        if error:
            return error, status_code

        reservas, total = filtrar_reservas(filtros, limit, offset)
        base_url = request.host_url.rstrip('/') + request.path
        links = armar_links(base_url, filtros, limit, offset, total)

        if len(reservas) == 0:
            return "", 204

        return {"reservas": reservas, "_links": links}, 200
    except Exception as exc:
        return error_respuesta(
            "Error interno del servidor",
            codigo="ERROR_INTERNO",
        ), 500


@reservas_bp.route('/reservas/<id_reserva>', methods=['GET'])
def obtener_reserva(id_reserva):
    try:
        error = validar_parametros()
        if error:
            return error

        id_numerico, error, status_code = validar_id(id_reserva)
        if error:
            return error, status_code

        return consultar_reserva(id_numerico)
    except Exception as exc:
        return error_respuesta(
            "Error interno del servidor",
            codigo="ERROR_INTERNO",
        ), 500


@reservas_bp.route('/reservas/<id_reserva>/estado', methods=['PUT'])
def actualizar_estado(id_reserva):
    try:
        error = validar_parametros()
        if error:
            return error

        id_numerico, error, status_code = validar_id(id_reserva)
        if error:
            return error, status_code

        datos, error, status_code = obtener_datos_json()
        if error:
            return error, status_code

        errores, estado = validar_estado_reserva(datos)
        if errores:
            return respuesta_validacion(errores)

        return procesar_estado_reserva(id_numerico, estado)
    except Exception as exc:
        return error_respuesta(
            "Error interno del servidor",
            codigo="ERROR_INTERNO",
        ), 500
