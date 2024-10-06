# Seccion de importe de librerias
# Importe de librerias de flask
from flask import Blueprint
from flask import request
from flask import jsonify
# Importe de cliente de ros
from api.utils import ros_connection
from api.utils.utils_functions import getInitialPose
# Importe de libreria de ros
import roslibpy

# Creacion de seccion para llamado blueprints
interact_bp = Blueprint('interact_bp', __name__)

# endpoint de ejecucion de stop panico
@interact_bp.route('/panic', methods = ["POST"])
def stopAll():
    try:
        # Llamado a ejecucion de servicio
        response = ros_connection.services["stop_all"].call(roslibpy.ServiceRequest({}))
        #response = service_panicButton.call(roslibpy.ServiceRequest({}))
        # Salida de mesnaje de ejecucion culminada
        return jsonify({
            'message': 'All movements stopped',
            # 'text': generated_api_calls
        }), 200
    except Exception as e:
        # Manejar cualquier excepción que ocurra durante el proceso
        return jsonify({"error": str(e)}), 500
    
# Funcion para reinicializacion de posicion en el mapa
@interact_bp.route('/retinit_pose', methods = ["POST"])
def retinit_pose():
    try:
        # Solicitud de posicion inicial por defecto
        pose_inicial = getInitialPose()
        # Llamado a ejecucion de servicio
        response = ros_connection.services["set_initial_pose"].call(roslibpy.ServiceRequest({"pose" : pose_inicial}))
        # Salida de mesnaje de ejecucion culminada
        return jsonify({
            'message': 'Assigned position initialized successfully.',
            # 'text': generated_api_calls
        }), 200
    except Exception as e:
        # Manejar cualquier excepción que ocurra durante el proceso
        return jsonify({"error": str(e)}), 500