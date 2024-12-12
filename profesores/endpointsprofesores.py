from flask import Blueprint, request, jsonify
from .modelsprofesores import Profesor 
from database import db
# Crear un Blueprint llamado 'profesores'
# Los Blueprints permiten separar po rmódulos
profesores_bp = Blueprint('profesores', __name__)

# Función de validación para profesores
def validar_profesor(data):
    campos_requeridos = ['numeroEmpleado', 'nombres', 'apellidos', 'horasClase']
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
    profesores = Profesor.query.all()  # Recupera todos los registros
    return jsonify([{
        "id": profesor.id,
        "numeroEmpleado": profesor.numeroEmpleado,
        "nombres": profesor.nombres,
        "apellidos": profesor.apellidos,
        "horasClase": profesor.horasClase
    } for profesor in profesores]), 200

# GET /profesores/{id}
@profesores_bp.route('/profesores/<int:id>', methods=['GET'])
def obtener_profesor_por_id(id):
    profesor = Profesor.query.get(id)
    if not profesor:
        return jsonify({"error": "Teacher not found"}), 404

    return jsonify({
        "id": profesor.id,
        "numeroEmpleado": profesor.numeroEmpleado,
        "nombres": profesor.nombres,
        "apellidos": profesor.apellidos,
        "horasClase": profesor.horasClase
    }), 200


# POST /profesores
@profesores_bp.route('/profesores', methods=['POST'])
def crear_profesor():
    datos = request.get_json()
    campos_requeridos = ['numeroEmpleado', 'nombres', 'apellidos', 'horasClase']
    for campo in campos_requeridos:
        if campo not in datos or not datos[campo]:
            return jsonify({"error": f"The field {campo} is required and cannot be empty."}), 400

    # Validar si el número de empleado ya existe
    if Profesor.query.filter_by(numeroEmpleado=datos['numeroEmpleado']).first():
        return jsonify({"error": "Employee number already exists"}), 400

    nuevo_profesor = Profesor(
        numeroEmpleado=datos['numeroEmpleado'],
        nombres=datos['nombres'],
        apellidos=datos['apellidos'],
        horasClase=datos['horasClase']
    )
    db.session.add(nuevo_profesor)
    db.session.commit()

    return jsonify({
        "id": nuevo_profesor.id,
        "numeroEmpleado": nuevo_profesor.numeroEmpleado,
        "nombres": nuevo_profesor.nombres,
        "apellidos": nuevo_profesor.apellidos,
        "horasClase": nuevo_profesor.horasClase
    }), 201



# PUT /profesores/{id}
@profesores_bp.route('/profesores/<int:id>', methods=['PUT'])
def actualizar_profesor(id):
    datos = request.get_json()
    campos_requeridos = ['nombres', 'horasClase']
    
    # Validar que los campos requeridos estén presentes y no sean nulos
    for campo in campos_requeridos:
        if campo not in datos or datos[campo] is None:
            return jsonify({"error": f"The field {campo} is required and cannot be empty."}), 400

    try:
        # Verificar que el profesor exista
        profesor = Profesor.query.get(id)
        if not profesor:
            return jsonify({"error": "Professor not found"}), 404

        # Actualizar los campos
        profesor.nombres = datos['nombres']
        profesor.horasClase = datos['horasClase']
        db.session.commit()

        return jsonify({
            "id": profesor.id,
            "nombres": profesor.nombres,
            "horasClase": profesor.horasClase
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500




# DELETE /profesores/{id}
@profesores_bp.route('/profesores/<int:id>', methods=['DELETE'])
def eliminar_profesor(id):
    profesor = Profesor.query.get(id)
    
    # Validar si el profesor existe
    if not profesor:
        return jsonify({"error": "Teacher not found"}), 404

    try:
        # Eliminar el profesor
        db.session.delete(profesor)
        db.session.commit()

        # Retornar una respuesta exitosa
        return jsonify({"message": "Teacher successfully deleted"}), 200

    except Exception as e:
        # Manejo de errores en caso de problemas al eliminar
        return jsonify({"error": str(e)}), 500


#prueba de base de datos
@profesores_bp.route('/test-db', methods=['GET'])
def test_db():
    try:
        db.session.execute('SELECT 1')
        return jsonify({"status": "Database connected successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
