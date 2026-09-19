import os

from dotenv import load_dotenv

# Carga las variables del archivo .env (si existe) sin pisar las del sistema
load_dotenv()


class Config:
    # Base de datos MySQL
    DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
    DB_PORT = int(os.getenv('DB_PORT', '3306'))
    DB_NAME = os.getenv('DB_NAME', 'club_deportivo')
    DB_USER = os.getenv('DB_USER', 'app_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'app_password')
    DB_ROOT_PASSWORD = os.getenv('DB_ROOT_PASSWORD', 'root_password')
    DB_SCHEMA_PATH = os.getenv('DB_SCHEMA_PATH', 'database/init_db.sql')

    # Servidor Flask
    FLASK_HOST = os.getenv('FLASK_HOST', '127.0.0.1')
    FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'

    # Seguridad
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave-de-desarrollo')