import os

from dotenv import load_dotenv

# Carga las variables del archivo .env (si existe) sin pisar las del sistema
load_dotenv()

class Config:
    # Base de datos
    DB_PATH = os.getenv('DB_PATH', 'database/canchas.db')
    DB_SCHEMA_PATH = os.getenv('DB_SCHEMA_PATH', 'database/init_db.sql')

    # Servidor Flask
    FLASK_HOST = os.getenv('FLASK_HOST', '127.0.0.1')
    FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'