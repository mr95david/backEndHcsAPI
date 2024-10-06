# import de librerias
from api.services.deepgram_service import DeepgramService
from api.utils import RECORD_FOLDER
from api.utils import RECORD_FILE
# Llamado de funciones de flask
from flask import Blueprint
from flask import request
from flask import jsonify
# Librerias utilitarias
from time import sleep
import os


# Creacion de routa de interaccion con aplicacion general
deepgram_bp = Blueprint('deepgram_bp', __name__)

# Carga de llave de api desde la configuracion o variables de entorno
DEEP_API = os.getenv('DEEPGRAM_API_KEY', "Deepgramm key")

# Creacion de cliente de deepgram desde el servicio propio
deepgram_client = DeepgramService(DEEP_API)

# Funcion para almacenamiento de audio
@deepgram_bp.route('/upload', methods = ['POST'])
def uploadAudio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Validar posibles extensiones de archivos de audio
    allowed_extensions = {'wav', 'mp3', 'm4a'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({'error': 'Formato de archivo no permitido. Solo se permiten archivos de audio'}), 400
    
    # Almacenamiento de audio recibido por frontend
    file_path = os.path.join(RECORD_FOLDER, file.filename)
    file.save(file_path)

    # Validacion de ejecucion de procedimiento
    try:
        # Proceso de transcripcion
        words = deepgram_client.transcription(file_path)
        print(words)
        #deepgram_client.trascription(RECORD_FILE)

        return jsonify({
            'message': 'File uploaded successfully',
            'path': file_path,
            'transcription': words
        }), 200
    except Exception as e:
        # Manejo de errores de transcripción
        return jsonify({'error': str(e)}), 500