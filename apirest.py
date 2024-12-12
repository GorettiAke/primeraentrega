from flask import Flask, jsonify
from database import db
from profesores.endpointsprofesores import profesores_bp
from alumnos.endpointsalumnos import s3_bp 
from alumnos.endpointsalumnos import sesiones_bp
from alumnos.endpointsalumnos import alumnos_bp
from alumnos.endpointsalumnos import sns_bp



app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy con la aplicación Flask
db.init_app(app)

# Crear las tablas al iniciar la aplicación
with app.app_context():
    db.create_all()

# Registrar los Blueprints
app.register_blueprint(sns_bp)
app.register_blueprint(alumnos_bp)
app.register_blueprint(profesores_bp)
app.register_blueprint(s3_bp)  # Registrar el nuevo blueprint de S3
app.register_blueprint(sesiones_bp)
# Manejo de errores
@app.errorhandler(405)
def metodo_no_permitido(e):
    return jsonify({"error": "Method not allowed"}), 405

@app.errorhandler(404)
def ruta_no_encontrada(e):
    return jsonify({"error": "Route not found"}), 404

@app.errorhandler(500)
def error_interno(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)
