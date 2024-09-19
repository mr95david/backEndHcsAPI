# Seccion de importe de librerias
from openai import OpenAI
# Librerias de validacion de paramteros
from typing import Any
from typing import Dict
from typing import List
# Librerias propias
from . import api_funct
from . import CONFIG_AGENT
from . import SYSTEM_DESC_PE
# Manejo de archivos json
import json

# Clase de ejecucion general de funciones
class OpenAIInterfaceFunctions:
    def __init__(self, key: str, api: Any = api_funct) -> None:
        # asignacion de variables de instancia
        self.api_List = api
        # Verificar mejor practica para manejo de informacion historica de robot
        self.chat_history_ = []
        # Condiguracion para sistema de agente de ia - Personalidad
        self.system_prompt_ = SYSTEM_DESC_PE

        # Inicializacion de cliente
        self.client = OpenAI(api_key = key)

    # Funcion para procesamiento de pregunta especifica de usuario
    def promptToCall(self, prompt: str, params: dict = CONFIG_AGENT):
        # descrcipcion de mensajes de entrada para el agente de ia
        params["messages"] = [
            {"role": "system", "content": self.system_prompt_},
            {"role": "user", "content": prompt},
        ]

        # Uso especifico de herramientas disponibles
        params["tools"] = self.api_List

        # Intento de ejecucion de de completions
        try:
            response = self.client.chat.completions.create(
                **params
            )
        except Exception as e:
            print(f"Oops! Something went wrong with {e}.")
            #self.chat_history_.pop()
            return []
        
        # Compilacion de contenido final
        final_content = response.choices[0].message.tool_calls
        return self.post_process_response(final_content)
    
    # Funcion para procesar la respuesta dada por el sistema de completions de chat
    def post_process_response(self, chat_response:list):
        # Organizacion de respuesta desde el esquema propuesto de json
        #print(chat_response)
        transform_response= []
        for iter in chat_response:
            dict_temp=dict()
            dict_temp["service"] = iter.function.name
            dict_temp["args"] = json.loads(iter.function.arguments)

            if iter.function.name == "enable_object_detection":
                 dict_temp["args"]['data'] = dict_temp["args"]['data'] == "True"

            if "linear:" in dict_temp["args"].keys():
                dict_temp["args"]['linear'] = dict_temp["args"].pop('linear:')

            
            transform_response.append(dict_temp)
        # transform_response = [
        #     {"service": iter.function.name, "args": json.loads(iter.function.arguments)}
        #     for iter in chat_response
        # ]
        #print(transform_response)
        return transform_response
