from database import db

class Profesor(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Autoincremento
    numeroEmpleado = db.Column(db.String(20), unique=True, nullable=False)
    nombres = db.Column(db.String(50), nullable=False)
    apellidos = db.Column(db.String(50), nullable=False)
    horasClase = db.Column(db.Integer, nullable=False)

