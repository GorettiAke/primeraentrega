from database import db
class Alumno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    matricula = db.Column(db.String(50), unique=True, nullable=False)
    promedio = db.Column(db.Float, nullable=False)
    fotoPerfilUrl = db.Column(db.String(255))  # Campo para la URL de la foto de perfil
    password = db.Column(db.String(255), nullable=False)


