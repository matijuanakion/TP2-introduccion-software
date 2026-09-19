from flask import Flask

from src.routes.canchas_routes import canchas_bp
from src.routes.deportes_routes import deportes_bp
from src.config import Config

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
app.json.ensure_ascii = False


app.register_blueprint(canchas_bp)
app.register_blueprint(deportes_bp)

# --- ARRANQUE DEL SERVIDOR ---
if __name__ == '__main__':
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG)