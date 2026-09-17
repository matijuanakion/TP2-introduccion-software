from flask import Blueprint

deportes_bp = Blueprint('deportes_bp', __name__)


@deportes_bp.route('/deportes', methods=['GET'])
def obtener_deportes():
    # El Swagger pide que los deportes sean diccionarios con id y nombre
    deportes = [
        {"id": 1, "nombre": "Futbol"},
        {"id": 2, "nombre": "Tenis"},
        {"id": 3, "nombre": "Padel"}
    ]
    return {"deportes": deportes}, 200

