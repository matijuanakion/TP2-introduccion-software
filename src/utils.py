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