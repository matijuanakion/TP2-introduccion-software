from flask import Flask

# Inicializa la aplicación
app = Flask(__name__)

# Define el endpoint y el método HTTP
@app.route('/deportes', methods=['GET'])
def obtener_deportes():
    return {"deportes": ["futbol", "tenis", "padel"]}, 200                      # Devuelve un JSON y el código de éxito 200

# Arranca el servidor
if __name__ == '__main__':
    app.run(debug=True)