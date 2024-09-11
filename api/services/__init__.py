# Importe de librerias 
from api.utils import SERVICE_PATH
from glob import glob
import json

# Creacion de inicializacion de instrucciones dadas por los mensajes de servicios
api_ = []
for api_file in glob(f"{SERVICE_PATH}/*.json"):
    with open(api_file, "r") as f:
        api_.append(json.load(f))