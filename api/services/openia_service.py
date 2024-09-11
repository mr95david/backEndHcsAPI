# Seccion de importe de librerias
from openai import OpenAI
# Librerias de validacion de paramteros
from typing import Any
from typing import Dict
from typing import List
# Librerias propias
from . import api_
# Manejo de archivos json
import json

# Creacion de clase de interface de interaccion con api openIA
class OpenAIInterface:
    def __init__(self, key: str, api: Any = api_) -> None:
        # asignacion de variables de instancia
        self.api_ = api
        self.chat_history_ = []
        # Condiguracion para sistema de agente de ia - Personalidad
        self.system_prompt_ = f"\
            Use this JSON schema to achieve the user's goals:\n\
            {str(api)}\n\
            Respond as a list of JSON objects.\
            Do not include explanations or conversation in the response.\
        "

        # Inicializacion de cliente
        self.client = OpenAI(api_key = key)

    # Funcion para procesamiento de ordenes
    def promptToApiCalls(self, prompt: str, model: str = "gpt-3.5-turbo", temperature: float = 0.8) -> List[Dict]:
        """Turns prompt into API calls.

        Args:
            prompt (str): Prompt.
            model (str, optional): OpenAI model. Defaults to "gpt-3.5-turbo".
            temperature (float, optional): OpenAI temperature. Defaults to 0.7.

        Returns:
            Dict: API calls.
        """

        # Seccion de historico de chat
        self.chat_history_.append(  # prompt taken from https://github.com/Significant-Gravitas/Auto-GPT/blob/master/autogpt/prompts/default_prompts.py
            {
                "role": "user",
                "content": f"\
                    {prompt}\n\
                    Respond only with the output in the exact format specified in the system prompt, with no explanation or conversation.\
                ",
            }
        )

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": self.system_prompt_}]
                + self.chat_history_,
                temperature=temperature,
                n=1,
            )
        except Exception as e:
            print(f"Oops! Something went wrong with {e}.")
            self.chat_history_.pop()
            return []

        self.chat_history_.append(
            {"role": "assistant", "content": response.choices[0].message.content}
        )

        # Validacion de contenido de respuesta obtenida
        content = self.chat_history_[-1]["content"]
        
        # Retrono de respuesta
        return self.post_process_response_(content)
    
    # Funcion para transformacion de respuesta obtenida de ia
    def post_process_response_(self, gpt_response: str) -> List[Dict]:
        """Applies some simple post-processing to the GPT response.

        Args:
            gpt_response (str): GPT response.

        Returns:
            List[Dict]: Post-processed response.
        """
        gpt_response = gpt_response.replace("'", '"')
        gpt_response = json.loads(gpt_response)

        # Condicional de tipo de respuesta 
        if isinstance(gpt_response, list):
            return gpt_response
        else:
            return [gpt_response]