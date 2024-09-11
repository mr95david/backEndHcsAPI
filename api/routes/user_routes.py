# Seccion de importe de librerias
from flask import Blueprint
from flask import request
from flask import jsonify
# Importe de modelos
from api.models import users
from api import db
# Importe de librerias utilitarias
import os

# Creacion de blue print, seccion de llamado a funciones de manipulacion de usuarios
user_bp = Blueprint('user_bp', __name__)

# Funcion destinada a la adicion de entradas de usuario:
@user_bp.route('/users', methods = ['GET'])
@user_bp.route('/get_users', methods = ['GET'])
def getUsers():
    # Validacion de errores 
    try:
        # Consultar todos los usuarios en la base de datos
        users_ = users.query.all()
        
        # Formatear los usuarios en un diccionario para convertir a JSON
        resultado = [
            {
                "id": user.id_value,
                "name": user.name,
                "lastname": user.lastname,
                "age": user.age,
                "profession": user.profession,
                "sexo": user.sexo,
                "user_path": user.user_path,
                "audio_path": user.audio_path,
                "transcription_path": user.transcription_path,
                "ia_path": user.ia_path
            } for user in users_
        ]
        
        # Devolver la lista de usuarios en formato JSON
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# funcion para agregar usuarios
@user_bp.route('/set_user', methods=['POST'])
def set_user():
    # Asignacion de valores de entrada
    data = request.get_json()
    
    # Validacion de entrada de datos obligatorios
    if not all([data.get('name'), data.get('lastname'), data.get('age'), data.get('profession'), data.get('sexo')]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400
    
    # Validacion de enteros, para edad
    try:
        age = int(data['age'])
        if age <= 0:
            raise ValueError
    except ValueError:
        return jsonify({"error": "La edad debe ser un número entero positivo"}), 400
    
    # Validacion de usuario unico
    existing_user = users.query.filter_by(name=data['name'], lastname=data['lastname']).first()
    if existing_user:
        return jsonify({"error": "El usuario con ese nombre y apellido ya existe"}), 409  # 409 Conflict


    user_path_value = f'./user_path/{data["name"]}_{data["lastname"]}_{data["age"]}'
    audio_path_value = f'./audio_{data["name"]}'
    transcription_path_value = f'./transcription_{data["name"]}'
    ia_path_value = f'./ia_{data["name"]}'
    # Creacion de nuevo campo que se ingresa a la base de datos
    new_user = users(
        name=data['name'],
        lastname=data['lastname'],
        age=age,
        profession=data['profession'],
        sexo=data['sexo'],
        user_path=user_path_value,#f'/user_path/{data["name"]}_{data["lastname"]}',
        audio_path=audio_path_value, #f'/audio_{data["name"]}',
        transcription_path=transcription_path_value,#f'/transcription_{data["name"]}',
        ia_path=ia_path_value#f'/ia_{data["name"]}'
    )

    try:
        db.session.add(new_user)
        db.session.commit()

        # Creacion de carpetas de almacenamiento de datos
        os.makedirs(user_path_value, exist_ok = True)
        os.makedirs(os.path.join(user_path_value, audio_path_value), exist_ok = True)
        os.makedirs(os.path.join(user_path_value, transcription_path_value), exist_ok = True)
        os.makedirs(os.path.join(user_path_value, ia_path_value), exist_ok = True)
        
        return jsonify({
            "message": "Nuevo usuario creado correctamente.",
            "id": new_user.id_value,
            "name": f"{new_user.name} {new_user.lastname}"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
# Funcion para borrado de usuario en caso de ser necesario
@user_bp.route('/delete_user', methods = ["DELETE"])
def deleteUser():
    # Lectura de valores ingresados - query params
    user_id = request.args.get('id_value')
    nombre = request.args.get('name')
    apellido = request.args.get('lastname')

    # Validacion de ingreso de datos para la eliminacion
    if not user_id and not (nombre and apellido):
        return jsonify({"error": "Debe proporcionar un id o el nombre y apellido para eliminar al usuario"}), 400

    # Buscar el usuario por ID, si se proporciona
    if user_id:
        usuario = users.query.filter_by(id_value=user_id).first()
    else:
        # Buscar el usuario por nombre y apellido si no se proporciona ID
        usuario = users.query.filter_by(name=nombre, lastname=apellido).first()

    # Verificar si el usuario existe
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    try:
        # Eliminar el usuario si existe
        db.session.delete(usuario)
        db.session.commit()
        return '', 204  # 204 No Content para indicar eliminación exitosa
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500  # Devolver error si hay algún problema

# Endpoint para validar si un usuario existe por nombre y apellido
@user_bp.route('/validate_user', methods=['GET'])
def validate_user():
    # Obtener los parámetros de nombre y apellido desde la solicitud
    
    name = request.args.get('name')
    lastname = request.args.get('lastname')
    # Asignacion de valores de entrada
    #data = request.get_json()

    # Validar que ambos parámetros se hayan proporcionado
    if not name or not lastname:
        return jsonify({"error": "Se requiere tanto el nombre como el apellido para la validación."}), 400

    try:
        # Buscar el usuario en la base de datos
        user = users.query.filter_by(name=name, lastname=lastname).first()

        # Si el usuario existe, devolver un mensaje positivo
        if user:
            return jsonify({"message": "Usuario encontrado", "id": user.id_value}), 200
        else:
            return jsonify({"message": "Usuario no encontrado", "id": 0}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500