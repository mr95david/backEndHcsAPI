# Import libraries
from flask import Blueprint
from flask import jsonify
# from api.model.welcome import WelcomeModel

# Asignacion de main
index = Blueprint('main', __name__)

# Creacion de ruta
@index.route('/')
@index.route('/index')
def getIndex():
    try:
        return jsonify({
                'message': 'Aplicacion en linea. Lista para ser ejecutada',
                #'api_response': generated_api_calls
            }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500