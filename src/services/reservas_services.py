from src.repositories.reservas_repositories import (
    contar_reservas,
    obtener_reservas_paginadas,
)


def filtrar_reservas(filtros, limit, offset):
    reservas = obtener_reservas_paginadas(filtros, limit, offset)
    total = contar_reservas(filtros)
    return reservas, total
