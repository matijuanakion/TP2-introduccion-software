from datetime import datetime

from flask import Blueprint, request

from src.errores import error_respuesta
from src.services.reservas_services import filtrar_reservas
from src.utils import armar_links, obtener_paginacion, validar_parametros


reservas_bp = Blueprint('reservas_bp', __name__)


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

        filtros = {}

        for campo in ('id_cancha', 'id_socio'):
            valor = request.args.get(campo)
            if valor is not None:
                if not valor.isascii() or not valor.isdecimal() or int(valor) <= 0:
                    return error_respuesta(
                        f"El parámetro '{campo}' debe ser un entero positivo",
                        codigo=f"{campo.upper()}_INVALIDO",
                    ), 400
                filtros[campo] = int(valor)

        estado = request.args.get('estado')
        if estado is not None:
            estados_validos = ('confirmada', 'cancelada', 'finalizada')
            if estado not in estados_validos:
                return error_respuesta(
                    "El parámetro 'estado' debe ser confirmada, cancelada o finalizada",
                    codigo="ESTADO_INVALIDO",
                ), 400
            filtros['estado'] = estado

        fechas = {}
        for campo in ('fecha_desde', 'fecha_hasta'):
            valor = request.args.get(campo)
            if valor is not None:
                try:
                    datetime.strptime(valor, '%Y-%m-%d')
                except ValueError:
                    return error_respuesta(
                        f"El parámetro '{campo}' debe tener formato YYYY-MM-DD",
                        codigo="FECHA_INVALIDA",
                    ), 400
                fechas[campo] = valor

        if (
            fechas.get('fecha_desde') is not None
            and fechas.get('fecha_hasta') is not None
            and fechas['fecha_desde'] > fechas['fecha_hasta']
        ):
            return error_respuesta(
                "'fecha_desde' debe ser menor o igual que 'fecha_hasta'",
                codigo="RANGO_FECHAS_INVALIDO",
            ), 400

        filtros.update(fechas)

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
