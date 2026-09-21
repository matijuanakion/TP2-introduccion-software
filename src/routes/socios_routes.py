from flask import Blueprint, request

from src.errores import error_respuesta
from src.services.socios_services import (
    consultar_socio,
    filtrar_socios,
    procesar_nuevo_socio,
)
from src.utils import armar_links, obtener_paginacion, validar_parametros

socios_bp = Blueprint('socios_bp', __name__)


@socios_bp.route('/socios/<id_socio>', methods=['GET'])
def obtener_socio(id_socio):
    try:
        error = validar_parametros()

        if error:
            return error

        try:
            id_numerico = (
                int(id_socio)
                if id_socio.isascii() and id_socio.isdecimal()
                else 0
            )
        except ValueError:
            id_numerico = 0

        if id_numerico <= 0:
            return error_respuesta(
                "El parámetro 'id' debe ser un entero positivo",
                codigo="ID_INVALIDO",
            ), 400

        respuesta, status_code = consultar_socio(id_numerico)
        return respuesta, status_code
    except Exception as exc:
        return error_respuesta(
            "Error interno del servidor",
            codigo="ERROR_INTERNO",
            descripcion=str(exc),
        ), 500


@socios_bp.route('/socios', methods=['POST'])
def crear_socio():
    try:
        datos = request.get_json()

        if not datos:
            return error_respuesta("El cuerpo de la solicitud no puede estar vacío"), 400

        respuesta, status_code = procesar_nuevo_socio(datos)
        return respuesta, status_code
    except Exception as exc:
        return error_respuesta(
            "Error interno del servidor",
            codigo="ERROR_INTERNO",
            descripcion=str(exc),
        ), 500


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