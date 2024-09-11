# Seccion de importe de librerias
from api import db

# Creacion de cada clase de modelo de tabla de la base de datos
class users(db.Model):
    __tablename__ = 'data_users'
    # Columnas para la tabla de la base de datos
    id_value = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    profession = db.Column(db.String(50), nullable=False)
    sexo = db.Column(db.String(50), nullable=False)
    # Columnas de ruta de almacenamiento de datos de cada usuario
    user_path = db.Column(db.String(200), nullable=False)
    audio_path = db.Column(db.String(200), nullable=False)
    transcription_path = db.Column(db.String(200), nullable=False)
    ia_path = db.Column(db.String(200), nullable=False)