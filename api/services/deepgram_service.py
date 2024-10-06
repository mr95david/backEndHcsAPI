# Seccion de importe de librerias
from deepgram import DeepgramClient
# Configuraciones de cliente de deepgram
from deepgram import PrerecordedOptions
from deepgram import FileSource
# Libreria para validacion de entrada de datos
from typing import Union
from typing import AnyStr
from os import PathLike

# Clase para la creacion de la conexion de deepgram
class DeepgramService:
    def __init__(self, api_key: AnyStr) -> None:
        self.client = DeepgramClient(api_key)

        # Configuracion de opciones de cliente
        self.options_ = PrerecordedOptions(
            model = "nova-2",
            smart_format = True,
            language = 'pt-br',
            # pt-br
        )

    # Funcion de transcripcion de grabacion realizada
    def transcription(self, file_name: Union[Union[str, bytes, PathLike[str], PathLike[bytes]], int]):
        try:
            with open(file_name,"rb") as audio:
                # Fuente de audio recibido
                source: FileSource = {"buffer": audio, "mimetype": "audio/wav"}
                # Solicitud de transcripcion a cliente de deepgram
                response = self.client.listen.prerecorded.v("1").transcribe_file(source, self.options_)

            return response.results["channels"][0]["alternatives"][0]["transcript"]
            
        except Exception as e:
            return {"error": str(e)}
        
        