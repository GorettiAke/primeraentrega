from flask import Blueprint, request, jsonify
from .models import Alumno, alumnos

# Crear un Blueprint llamado 'alumnos'
# Los Blueprints permiten que se separe por modulos, separando las rutas y la lógica en componentes que se puedan usar de nuevo
alumnos_bp = Blueprint('alumnos', __name__)

# Función de validación para alumnos
def validar_alumno(data):
    campos_requeridos = ['id', 'nombres', 'apellidos', 'matricula', 'promedio']
    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return False, f"The field {campo} is required and cannot be empty."
        if campo == 'promedio' and not isinstance(data[campo], (int, float)):
            return False, "The average must be a number."
    return True, ""

# Endpoints para alumnos

# GET /alumnos
@alumnos_bp.route('/alumnos', methods=['GET'])
def obtener_alumnos():
    return jsonify([alumno.__dict__ for alumno in alumnos]), 200

# GET /alumnos/{id}
@alumnos_bp.route('/alumnos/<int:id>', methods=['GET'])
def obtener_alumno(id):
    alumno = next((a for a in alumnos if a.id == id), None)
    if alumno is None:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(alumno.__dict__), 200

# POST /alumnos
@alumnos_bp.route('/alumnos', methods=['POST'])
def crear_alumno():
    datos = request.get_json()
    valido, mensaje = validar_alumno(datos)
    if not valido:
        return jsonify({"error": mensaje}), 400
    nuevo_alumno = Alumno(**datos)
    alumnos.append(nuevo_alumno)
    return jsonify(nuevo_alumno.__dict__), 201

# PUT /alumnos/{id}
@alumnos_bp.route('/alumnos/<int:id>', methods=['PUT'])
def actualizar_alumno(id):
    datos = request.get_json()
    valido, mensaje = validar_alumno(datos)
    if not valido:
        return jsonify({"error": mensaje}), 400
    alumno = next((a for a in alumnos if a.id == id), None)
    if alumno is None:
        return jsonify({"error": "Student not found"}), 404
    alumno.__dict__.update(datos)
    return jsonify(alumno.__dict__), 200

# DELETE /alumnos/{id}
@alumnos_bp.route('/alumnos/<int:id>', methods=['DELETE'])
def eliminar_alumno(id):
    global alumnos
    alumno = next((a for a in alumnos if a.id == id), None)
    if alumno is None:
        return jsonify({"error": "Student not found"}), 404
    alumnos = [a for a in alumnos if a.id != id]
    return '', 200
