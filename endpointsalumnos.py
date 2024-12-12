from flask import Blueprint, request, jsonify
from .modelsalumnos import Alumno
from database import db
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import boto3
from flask import request
from botocore.exceptions import NoCredentialsError
import uuid
import time
import random
import string

# Los Blueprints permiten que se separe por modulos, separando las rutas y la lógica en componentes que se puedan usar de nuevo
alumnos_bp = Blueprint('alumnos', __name__)
s3_bp = Blueprint('s3', __name__)
sns_bp = Blueprint('sns', __name__)
sesiones_bp = Blueprint('sesiones', __name__)
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:101534774345:uno'
BUCKET_NAME = 'my-giar'
REGION = 'us-east-1'  
# Credenciales obtenidas del laboratorio AWS Academy
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
AWS_SESSION_TOKEN = ""



dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN ,
    region_name='us-east-1'
)

# Define la tabla
table = dynamodb.Table('sesiones-alumnos')

# Función de validación para alumnos
def validar_alumno(data):
    campos_requeridos = ['nombres', 'apellidos', 'matricula', 'promedio']
    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return False, f"The field {campo} is required and cannot be empty."
    if 'promedio' in data and not isinstance(data['promedio'], (int, float)):
        return False, "The average must be a number."
    return True, ""


# Endpoints para alumnos

# GET /alumnos
@alumnos_bp.route('/alumnos', methods=['GET'])
def obtener_alumnos():
    try:
        # Consulta a la base de datos para obtener todos los alumnos
        alumnos = Alumno.query.all()

        # Serializar los datos
        alumnos_data = [
            {
                "id": alumno.id,
                "nombres": alumno.nombres,
                "apellidos": alumno.apellidos,
                "matricula": alumno.matricula,
                "promedio": alumno.promedio,
                "fotoPerfilUrl": alumno.fotoPerfilUrl,
            }
            for alumno in alumnos
        ]
        return jsonify(alumnos_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@alumnos_bp.route('/alumnos/<int:id>', methods=['GET'])
def obtener_alumno(id):
    alumno = Alumno.query.get(id)
    if not alumno:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({
        "id": alumno.id,
        "nombres": alumno.nombres,
        "apellidos": alumno.apellidos,
        "matricula": alumno.matricula,
        "promedio": alumno.promedio,
        "fotoPerfilUrl": alumno.fotoPerfilUrl
    }), 200


# POST /alumnos
@alumnos_bp.route('/alumnos', methods=['POST'])
def crear_alumno():
    datos = request.get_json()
    campos_requeridos = ['nombres', 'apellidos', 'matricula', 'promedio', 'password']
    for campo in campos_requeridos:
        if campo not in datos or not datos[campo]:
            return jsonify({"error": f"The field {campo} is required and cannot be empty."}), 400

    # Validar si la matrícula ya existe
    if Alumno.query.filter_by(matricula=datos['matricula']).first():
        return jsonify({"error": "Matricula already exists"}), 400

    # Encriptar la contraseña
    hashed_password = generate_password_hash(datos['password'])

    nuevo_alumno = Alumno(
        nombres=datos['nombres'],
        apellidos=datos['apellidos'],
        matricula=datos['matricula'],
        promedio=datos['promedio'],
        password=hashed_password
    )
    db.session.add(nuevo_alumno)
    db.session.commit()

    return jsonify({
        "id": nuevo_alumno.id,
        "nombres": nuevo_alumno.nombres,
        "apellidos": nuevo_alumno.apellidos,
        "matricula": nuevo_alumno.matricula,
        "promedio": nuevo_alumno.promedio
    }), 201

@alumnos_bp.route('/alumnos/<int:id>', methods=['PUT'])
def actualizar_alumno(id):
    datos = request.get_json()
    campos_requeridos = ['nombres', 'apellidos', 'matricula', 'promedio']
    for campo in campos_requeridos:
        if campo not in datos or not datos[campo]:
            return jsonify({"error": f"The field {campo} is required and cannot be empty."}), 400

    alumno = Alumno.query.get(id)
    if not alumno:
        return jsonify({"error": "Student not found"}), 404

    # Actualizar los campos
    alumno.nombres = datos['nombres']
    alumno.apellidos = datos['apellidos']
    alumno.matricula = datos['matricula']
    alumno.promedio = datos['promedio']
    db.session.commit()

    return jsonify({
        "id": alumno.id,
        "nombres": alumno.nombres,
        "apellidos": alumno.apellidos,
        "matricula": alumno.matricula,
        "promedio": alumno.promedio
    }), 200



# DELETE /alumnos/{id}
@alumnos_bp.route('/alumnos/<int:id>', methods=['DELETE'])
def eliminar_alumno(id):
    alumno = Alumno.query.get(id)
    if not alumno:
        return jsonify({"error": "Student not found"}), 404

    db.session.delete(alumno)
    db.session.commit()
    return '', 200

#para base de datos
@alumnos_bp.route('/test-ids', methods=['GET'])
def test_ids():
    alumnos = Alumno.query.all()
    return jsonify([{
        "id": alumno.id,
        "nombres": alumno.nombres
    } for alumno in alumnos]), 200

#para foto
@alumnos_bp.route('/alumnos/<int:id>/fotoPerfil', methods=['POST'])
def subir_foto_perfil(id):
    # Validar que el alumno exista
    alumno = Alumno.query.get(id)
    if not alumno:
        return jsonify({"error": "Student not found"}), 404

    # Validar que el archivo esté presente en la solicitud
    if 'foto' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['foto']
    file_name = f"alumnos/{id}/{file.filename}"  # Ruta personalizada para S3

    # Inicializar el cliente de boto3 con las credenciales
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_session_token=AWS_SESSION_TOKEN,
        region_name=REGION
    )

    try:
        # Subir archivo a S3
        s3.upload_fileobj(file, BUCKET_NAME, file_name)



        # Generar la URL pública del archivo
        file_url = f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{file_name}"

        # Actualizar la URL en la base de datos
        alumno.fotoPerfilUrl = file_url
        db.session.commit()

        return jsonify({
            "message": "Profile picture uploaded successfully",
            "fotoPerfilUrl": file_url
        }), 200  

    except NoCredentialsError:
        return jsonify({"error": "AWS credentials not available"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


#email


@alumnos_bp.route('/alumnos/<int:id>/email', methods=['POST'])
def enviar_email_alumno(id):
    # Validar que el alumno exista
    alumno = Alumno.query.get(id)
    if not alumno:
        return jsonify({"error": "Student not found"}), 404

    # Inicializar cliente SNS
    sns = boto3.client(
        'sns',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_session_token=AWS_SESSION_TOKEN,
        region_name=REGION
    )

    # Crear el mensaje a enviar
    mensaje = (
        f"Información del Alumno:\n"
        f"Nombre: {alumno.nombres} {alumno.apellidos}\n"
        f"Matrícula: {alumno.matricula}\n"
        f"Promedio: {alumno.promedio}\n"
    )

    try:
        # Publicar el mensaje en el Topic SNS
        response = sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=mensaje,
            Subject="Información del Alumno"
        )
        return jsonify({
            "message": "Email sent successfully",
            "SNS_Response": response
        }), 200

    except NoCredentialsError:
        return jsonify({"error": "AWS credentials not available"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#Este endpoint debe recibir la contraseña del alumno y compararla en la base de datos.
@alumnos_bp.route('/alumnos/<int:id>/session/login', methods=['POST'])
def login_sesion_alumno():
    try:
        # Obtener datos de la solicitud
        datos = request.get_json()
        if 'password' not in datos or not datos['password']:
            return jsonify({"error": "Password is required"}), 400

        # Verificar que el alumno exista
        alumno = Alumno.query.get(id)
        if not alumno:
            return jsonify({"error": "Student not found"}), 404

        # Verificar contraseña
        if not check_password_hash(alumno.password, datos['password']):
            return jsonify({"error": "Invalid password"}), 400  # Respuesta para contraseña incorrecta

        # Generar sessionString
        session_string = ''.join(random.choices(string.ascii_letters + string.digits, k=128))

        # Crear una nueva sesión en DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('sesiones-alumnos')

        session_id = str(uuid.uuid4())
        timestamp = int(time.time())

        table.put_item(
            Item={
                'id': session_id,
                'fecha': timestamp,
                'alumnoId': id,
                'active': True,
                'sessionString': session_string
            }
        )

        return jsonify({
            "message": "Login successful",
            "sessionString": session_string
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


#Debe recibir el sessionString y ver si la sesión es válida, debe comprar el valor de active:
@sesiones_bp.route('/alumnos/<int:id>/session/verify', methods=['POST'])
def verify_session(id):
    data = request.get_json()
    if 'sessionString' not in data:
        return jsonify({"error": "SessionString is required"}), 400

    try:
        # Consultar DynamoDB para verificar la sesión
        response = table.query(
            IndexName='sessionString-index',  # Si tienes un índice secundario global
            KeyConditionExpression='sessionString = :session',
            ExpressionAttributeValues={':session': data['sessionString']}
        )
        items = response.get('Items', [])

        if not items or items[0].get('alumnoId') != id or not items[0].get('active', False):
            return jsonify({"error": "Invalid or inactive session"}), 400

        return jsonify({"message": "Session is valid"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



#Debe recibir un sessionString y poner el valor de active en false.
@sesiones_bp.route('/alumnos/<int:id>/session/logout', methods=['POST'])
def logout_session(id):
    data = request.get_json()
    if 'sessionString' not in data:
        return jsonify({"error": "SessionString is required"}), 400

    # Buscar la sesión en DynamoDB
    response = table.scan(
        FilterExpression='alumnoId = :id AND sessionString = :session',
        ExpressionAttributeValues={
            ':id': id,
            ':session': data['sessionString']
        }
    )
    items = response.get('Items', [])

    if not items:
        return jsonify({"error": "Session not found"}), 404

    # Actualizar active a False
    session_id = items[0]['id']
    table.update_item(
        Key={'id': session_id},
        UpdateExpression="set active = :a",
        ExpressionAttributeValues={':a': False}
    )

    return jsonify({"message": "Session logged out"}), 200
