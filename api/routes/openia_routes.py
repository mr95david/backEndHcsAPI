# Seccion de importe de librerias
from api.services.openia_service import OpenAIInterface
from api.services.openai_functions import OpenAIInterfaceFunctions
from api.utils import RECORD_FOLDER
from api.utils import OPENIA_MODEL
# Llamado de funciones de flask
from flask import Blueprint
from flask import request
from flask import jsonify
# Modelo de base de datos
from api.models import users
from api.utils import ros_conn
from api import db
# Librerias utilitarias
from glob import glob
import json
import os
import threading
import shutil


# Creacion de objeto de interaccion de ruta
openia_bp = Blueprint('openia_bp', __name__)

# Carga de llave de api desde la configuracion o variables de entorno
OPEN_API = os.getenv('OPENIA_API_KEY', "Your key")

# Creacion de cliente de deepgram desde el servicio propio (Legacy)
# openia_client = OpenAIInterface(key = OPEN_API)
## Llamado de objeto de interface2
openia_client = OpenAIInterfaceFunctions(key = OPEN_API)

# Funcion para generacion de solicitud/orden dada por modelo llm
@openia_bp.route("/chat_request", methods = ["POST", "GET"])
def sendOrder():
    # Validacion general de ejecucion
    try:
         # Validación de entrada
        data = request.get_json()

        # Condicional de respuesta negativa dada por la falta de datos en la ejecucioin
        if not data or 'transcription' not in data or 'name' not in data or 'lastname' not in data:
            return jsonify({"error": "Faltan campos obligatorios (transcription, name, lastname)"}), 400
        
        # Asignacion de valores desde la solicitud dada
        name = data['name']
        lastname = data['lastname']
        transcription = str(data['transcription'])

        # Busqueda de usuario existente
        existing_user = users.query.filter_by(name = name, lastname = lastname).first()

        # Validacion de existencia de usuario
        if not existing_user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Asignacion de directorios de usuario
        path_user = existing_user.user_path
        path_audio = os.path.join(path_user, existing_user.audio_path)
        path_transcription = os.path.join(path_user, existing_user.transcription_path)
        path_ia = os.path.join(path_user, existing_user.ia_path)

        # Declaracion de audio existente
        exists_audio_path = os.path.join(RECORD_FOLDER, "recording.wav") 
        # Validacion de existencia
        if not os.path.exists(exists_audio_path):
            return jsonify({"error": "Audio file not found"}), 400

        # Seccion de organizacion de archivos existentes
        # Organizacion de archivos de audio
        audio_files_ = sorted(glob(os.path.join(path_audio, 'conversacion_*.wav')))
        audio_num = len(audio_files_) + 1
        audio_filename = f'conversacion_{audio_num}.wav'
        
        # Mover una copia del archivo de audio a la carpeta del usuario
        new_audio_path = os.path.join(path_audio, audio_filename)
        shutil.copy(exists_audio_path, new_audio_path)

        # Almacenamiento de datos de transcripcion
         # Actualizar el archivo JSON de transcripciones en la carpeta de conversaciones
        transcription_json_path = os.path.join(path_transcription, 'conversations.json')
        
        if os.path.exists(transcription_json_path):
            with open(transcription_json_path, 'r', encoding='utf-8') as f:
                conversation_data = json.load(f)
        else:
            conversation_data = {}

        # Añadir la nueva transcripción
        conversation_data[f'conversacion_{audio_num}'] = {'data': transcription}

        # Guardar las transcripciones actualizadas
        with open(transcription_json_path, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, ensure_ascii=False, indent=4)
        
        # Procesamiento en chatgtp (legacy)
        # generated_api_calls = openia_client.promptToApiCalls(
        #     transcription, 
        #     model = OPENIA_MODEL
        # )

        # New metod for call funcion from user request 
        generated_api_calls = openia_client.promptToCall(
            prompt = transcription
        )
        
        # Almacenar la respuesta del modelo en la carpeta texto
        existing_text_files = sorted(glob(os.path.join(path_ia, 'iaResponse_*.json')))
        text_num = len(existing_text_files) + 1
        text_filename = f'iaResponse_{text_num}.json'
        text_file_path = os.path.join(path_ia, text_filename)

        with open(text_file_path, 'w') as f:
            json.dump(generated_api_calls, f, indent=4)

        thread = threading.Thread(
            target = ros_conn.sendTask,
            args = (generated_api_calls,)
        )
        thread.start()

        return jsonify({
            'message': 'Archivo procesado correctamente',
            'transcription': transcription,
            'orders_list': generated_api_calls
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500