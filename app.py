from flask import Flask, request
from source.routes.canchas_routes import canchas_bp
from source.routes.deportes_routes import deportes_bp

app = Flask(__name__)


app.register_blueprint(canchas_bp)
app.register_blueprint(deportes_bp)

# --- ARRANQUE DEL SERVIDOR ---
if __name__ == '__main__':
    app.run(debug=True)