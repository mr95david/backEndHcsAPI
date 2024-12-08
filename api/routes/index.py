# Import libraries
from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import send_from_directory
from flask import Response
import os
# from api.model.welcome import WelcomeModel

# Asignacion de main
index = Blueprint('main', __name__, static_folder='static', template_folder='index.html')


@index.route('/index')
def getIndex():
    try:
        return jsonify({
                'message': 'Aplicacion en linea. Lista para ser ejecutada',
                #'api_response': generated_api_calls
            }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@index.route('/')
def getHome():
    return render_template('index.html')
