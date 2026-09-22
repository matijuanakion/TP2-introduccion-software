from flask import Blueprint, request

from src.errores import error_respuesta
from src.services.reservas_services import filtrar_reservas, procesar_nueva_reserva
from src.utils import (
    armar_links,
    obtener_datos_json,
    obtener_paginacion,
    validar_parametros,
)
from src.validators.reservas_validators import validar_filtros_reservas


reservas_bp = Blueprint('reservas_bp', __name__)


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
            descripcion=str(exc),
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
            return {
                'errors': [
                    {
                        'code': error['code'],
                        'message': error['message'],
                        'level': error.get('level', 'error'),
                        'description': error.get('description', error['message']),
                    }
                    for error in errores
                ]
            }, max(error.get('status', 400) for error in errores)

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
            descripcion=str(exc),
        ), 500
