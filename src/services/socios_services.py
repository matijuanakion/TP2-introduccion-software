from src.repositories.socios_repositories import (
    contar_socios,
    obtener_socios_paginados,
)


def filtrar_socios(filtros, limit, offset):
    socios = obtener_socios_paginados(filtros, limit, offset)
    total = contar_socios(filtros)
    return socios, total