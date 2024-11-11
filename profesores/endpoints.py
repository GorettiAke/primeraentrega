from flask import Blueprint, request, jsonify
from .models import Profesor, profesores

# Crear un Blueprint llamado 'profesores'
# Los Blueprints permiten separar po rmódulos
profesores_bp = Blueprint('profesores', __name__)

# Función de validación para profesores
def validar_profesor(data):
    campos_requeridos = ['id', 'numeroEmpleado', 'nombres', 'apellidos', 'horasClase']
    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return False, f"The field {campo} is required and cannot be empty."
        if campo == 'horasClase' and not isinstance(data[campo], int):
            return False, "Class hours must be an integer."
    return True, ""

# Endpoints para profesores

# GET /profesores
@profesores_bp.route('/profesores', methods=['GET'])
def obtener_profesores():
    return jsonify([profesor.__dict__ for profesor in profesores]), 200

# GET /profesores/{id}
@profesores_bp.route('/profesores/<int:id>', methods=['GET'])
def obtener_profesor(id):
    profesor = next((p for p in profesores if p.id == id), None)
    if profesor is None:
        return jsonify({"error": "Teacher not found"}), 404
    return jsonify(profesor.__dict__), 200

# POST /profesores
@profesores_bp.route('/profesores', methods=['POST'])
def crear_profesor():
    datos = request.get_json()
    valido, mensaje = validar_profesor(datos)
    if not valido:
        return jsonify({"error": mensaje}), 400
    nuevo_profesor = Profesor(**datos)
    profesores.append(nuevo_profesor)
    return jsonify(nuevo_profesor.__dict__), 201

# PUT /profesores/{id}
@profesores_bp.route('/profesores/<int:id>', methods=['PUT'])
def actualizar_profesor(id):
    datos = request.get_json()
    valido, mensaje = validar_profesor(datos)
    if not valido:
        return jsonify({"error": mensaje}), 400
    profesor = next((p for p in profesores if p.id == id), None)
    if profesor is None:
        return jsonify({"error": "Teacher not found"}), 404
    profesor.__dict__.update(datos)
    return jsonify(profesor.__dict__), 200

# DELETE /profesores/{id}
@profesores_bp.route('/profesores/<int:id>', methods=['DELETE'])
def eliminar_profesor(id):
    global profesores
    profesor = next((p for p in profesores if p.id == id), None)
    if profesor is None:
        return jsonify({"error": "Teacher not found"}), 404
    profesores = [p for p in profesores if p.id != id]
    return '', 200
