# Importe de librerias
from api.utils.ros_communication import RosClientManagerObject
import os

# Creacion de variables propias de clase
RECORD_FOLDER = './assets/current-record'
# Validacion y creacion de directorio
os.makedirs(RECORD_FOLDER, exist_ok = True)

# Ruta de almacenamiento y nombre de archivo de audio
RECORD_FILE = "./assets/current-record/recording.wav"

# Ruta de existencia de servicios
SERVICE_PATH = "./api/services/service_msgs/srv"
# Segunda opcion llamado de funrio
FUNCTIONS_PATH = "./api/services/functions/movement_functions"

# Modelo de conexion de ia
OPENIA_MODEL:str = "gpt-4o-mini"

# Creacion de conexion
ros_connection = RosClientManagerObject()