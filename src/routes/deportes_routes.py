from flask import Blueprint
from src.services.deportes_services import listar_deportes

deportes_bp = Blueprint('deportes_bp', __name__)


@deportes_bp.route('/deportes', methods=['GET'])
def obtener_deportes():
    deportes = listar_deportes()

    if len(deportes) == 0:
        return {"deportes": deportes}, 204

    return {"deportes": deportes}, 200