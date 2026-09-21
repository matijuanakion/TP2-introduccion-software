from flask import Blueprint

from src.errores import error_respuesta
from src.services.deportes_services import listar_deportes

deportes_bp = Blueprint('deportes_bp', __name__)


@deportes_bp.route('/deportes', methods=['GET'])
def obtener_deportes():
    try:
        deportes = listar_deportes()

        if len(deportes) == 0:
            return "", 204

        return {"deportes": deportes}, 200
    except Exception as exc:
        return error_respuesta(
            "Error interno del servidor",
            codigo="ERROR_INTERNO",
            descripcion=str(exc),
        ), 500