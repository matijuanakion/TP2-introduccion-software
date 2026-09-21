from flask import Blueprint, request

from src.errores import error_respuesta

from src.services.canchas_services import (
    consultar_cancha,
    filtrar_canchas,
    procesar_actualizacion_cancha,
    procesar_nueva_cancha,
)

from src.utils import armar_links, validar_parametros

canchas_bp = Blueprint('canchas_bp', __name__)

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

        filtros = {}

        id_deporte = request.args.get('id_deporte')
        if id_deporte is not None:
            if not id_deporte.isdigit():
                return error_respuesta("El parámetro 'id_deporte' debe ser un entero"), 400
            filtros['id_deporte'] = int(id_deporte)

        nombre = request.args.get('nombre')
        if nombre is not None:
            filtros['nombre'] = nombre

        for campo in ('techada', 'activa'):
            valor = request.args.get(campo)
            if valor is not None:
                if valor.lower() not in ('true', 'false'):
                    return error_respuesta(f"El parámetro '{campo}' debe ser true o false"), 400
                filtros[campo] = valor.lower() == 'true'

        try:
            limit = int(request.args.get('_limit', 10))
            offset = int(request.args.get('_offset', 0))
        except ValueError:
            return error_respuesta("Los parámetros '_limit' y '_offset' deben ser enteros"), 400

        if not 1 <= limit <= 100 or offset < 0:
            return error_respuesta(
            "'_limit' debe estar entre 1 y 100 y '_offset' ser mayor o igual a 0"
            ), 400

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
        datos = request.get_json()

        if not datos:
            return error_respuesta("El cuerpo de la solicitud no puede estar vacío"), 400

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

        try:
            id_numerico = (
                int(id_cancha)
                if id_cancha.isascii() and id_cancha.isdecimal()
                else 0
            )
        except ValueError:
            id_numerico = 0

        if id_numerico <= 0:
            return error_respuesta(
                "El parámetro 'id' debe ser un entero positivo",
                codigo="ID_INVALIDO",
            ), 400

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

        try:
            id_numerico = (
                int(id_cancha)
                if id_cancha.isascii() and id_cancha.isdecimal()
                else 0
            )
        except ValueError:
            id_numerico = 0

        if id_numerico <= 0:
            return error_respuesta(
                "El parámetro 'id' debe ser un entero positivo",
                codigo="ID_INVALIDO",
            ), 400

        datos = request.get_json(silent=True)
        if datos is None or not isinstance(datos, dict):
            return error_respuesta(
                "El cuerpo de la solicitud debe ser un objeto JSON",
                codigo="CUERPO_INVALIDO",
            ), 400

        return procesar_actualizacion_cancha(id_numerico, datos)
    except Exception as exc:
        return error_respuesta(
            "Error interno del servidor",
            codigo="ERROR_INTERNO",
            descripcion=str(exc),
        ), 500