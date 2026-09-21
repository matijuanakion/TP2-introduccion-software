from datetime import datetime

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
    validar_id,
    validar_parametros,
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

        fecha = request.args.get('fecha')
        hora_inicio = request.args.get('hora_inicio')
        hora_fin = request.args.get('hora_fin')

        if not fecha or not hora_inicio or not hora_fin:
            return error_respuesta(
                "Los parámetros 'fecha', 'hora_inicio' y 'hora_fin' son obligatorios",
                codigo="PARAMETRO_OBLIGATORIO",
            ), 400

        try:
            datetime.strptime(fecha, '%Y-%m-%d')
        except ValueError:
            return error_respuesta(
                "El parámetro 'fecha' debe tener formato YYYY-MM-DD",
                codigo="FECHA_INVALIDA",
            ), 400

        try:
            inicio = datetime.strptime(hora_inicio, '%H:%M:%S')
            fin = datetime.strptime(hora_fin, '%H:%M:%S')
        except ValueError:
            return error_respuesta(
                "Los parámetros 'hora_inicio' y 'hora_fin' deben tener formato HH:00:00",
                codigo="HORARIO_INVALIDO",
            ), 400

        if (
            len(hora_inicio) != 8
            or len(hora_fin) != 8
            or hora_inicio[2:] != ':00:00'
            or hora_fin[2:] != ':00:00'
        ):
            return error_respuesta(
                "Los horarios deben comenzar exactamente en una hora",
                codigo="HORARIO_INVALIDO",
            ), 400

        duracion = (fin - inicio).seconds // 3600
        if fin <= inicio or duracion not in (1, 2):
            return error_respuesta(
                "El intervalo debe durar una o dos horas y hora_inicio debe ser menor que hora_fin",
                codigo="DURACION_INVALIDA",
            ), 400

        filtros = {
            'fecha': fecha,
            'hora_inicio': hora_inicio,
            'hora_fin': hora_fin,
        }

        id_deporte = request.args.get('id_deporte')
        if id_deporte is not None:
            if not id_deporte.isdigit() or int(id_deporte) <= 0:
                return error_respuesta(
                    "El parámetro 'id_deporte' debe ser un entero positivo",
                    codigo="ID_DEPORTE_INVALIDO",
                ), 400
            filtros['id_deporte'] = int(id_deporte)

        techada = request.args.get('techada')
        if techada is not None:
            if techada.lower() not in ('true', 'false'):
                return error_respuesta(
                    "El parámetro 'techada' debe ser true o false",
                    codigo="TECHADA_INVALIDA",
                ), 400
            filtros['techada'] = techada.lower() == 'true'

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