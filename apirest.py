from flask import Flask, jsonify
from alumnos.endpoints import alumnos_bp
from profesores.endpoints import profesores_bp

app = Flask(__name__)

# Registrar los Blueprints
app.register_blueprint(alumnos_bp)
app.register_blueprint(profesores_bp)

# Manejo de errores para métodos no permitidos
@app.errorhandler(405)
def metodo_no_permitido(e):
    return jsonify({"error": "Method not allowed"}), 405

# Manejo de errores para rutas no encontradas
@app.errorhandler(404)
def ruta_no_encontrada(e):
    return jsonify({"error": "Route not found"}), 404

# Manejo de errores internos del servidor
@app.errorhandler(500)
def error_interno(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)
