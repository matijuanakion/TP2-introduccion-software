from flask import request

from src.errores import error_respuesta


def armar_href(base_url, filtros, limit, offset):
    parametros = []
    for campo, valor in filtros.items():
        if isinstance(valor, bool):
            valor = 'true' if valor else 'false'
        parametros.append(f"{campo}={valor}")
    parametros.append(f"_offset={offset}")
    parametros.append(f"_limit={limit}")
    return {"href": base_url + '?' + '&'.join(parametros)}


def armar_links(base_url, filtros, limit, offset, total):
    prev_offset = max(0, offset - limit) if offset > 0 else None
    next_offset = offset + limit if offset + limit < total else None
    last_offset = ((total - 1) // limit) * limit if total > 0 else 0

    return {
        "_first": armar_href(base_url, filtros, limit, 0),
        "_prev": armar_href(base_url, filtros, limit, prev_offset) if prev_offset is not None else None,
        "_next": armar_href(base_url, filtros, limit, next_offset) if next_offset is not None else None,
        "_last": armar_href(base_url, filtros, limit, last_offset),
    }


def obtener_paginacion():
    try:
        limit = int(request.args.get('_limit', 10))
        offset = int(request.args.get('_offset', 0))
    except ValueError:
        return None, None, error_respuesta(
            "Los parámetros '_limit' y '_offset' deben ser enteros"
        ), 400

    if not 1 <= limit <= 100 or offset < 0:
        return None, None, error_respuesta(
            "'_limit' debe estar entre 1 y 100 y '_offset' ser mayor o igual a 0"
        ), 400

    return limit, offset, None, None


def validar_parametros(permitidos=()):
    desconocidos = sorted(set(request.args) - set(permitidos))

    if desconocidos:
        return error_respuesta(
            f"Parámetros desconocidos: {', '.join(desconocidos)}",
            codigo="PARAMETRO_DESCONOCIDO",
        ), 400

    return None