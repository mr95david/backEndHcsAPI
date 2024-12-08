# Seccion de importe de librerias
# Librerias para conexion con ros
import roslibpy
# Importe de librerias de ejecucion de ciclos
import threading
# Importe de librerias utilitarias
from typing import List
from time import sleep
from json import load as jload
from os import getcwd

# Validacion de servicios existentes por cada clase de ejecucion de servicios
MOVECLASS = ["relative_move", "move_to_pose"]
VISUALCLASS = ["enable_object_detection", "object_to_detect"]
MANDATORYCLASS = ["stop_movement"]
INFORMATIONCLASS = ["reject_request"]

# Creacion de clase de ejecucion
class RosClientManagerObject:
    # Inicializador de clase
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 9090,
        msj:str = "A solicitação foi recebida corretamente."
    ):
        """
        Se crea la conexion de cliente, a partir de los parametros de entrada. Ademas se define.
        la lista de servicios disponibles para el uso de la clase.
        args:
            host: str -- Ruta de conexion con ros
            port: int -- Valor de puerta designada para la conexion
        """
        # Variables de instancia de clase
        self.host:str = host
        self.port:str = port
        self.services:dict = dict()
        self.moviment_list:list = list()
        self.visual_list:list = list()
        self.mandatory_list:list = list()
        # Variable de almacenamiento de ordenes del sistema
        self.system_task_list: list = list()
        # Variable de mensaje de respuesta 
        self.message = msj

        # Variables de validacion de estado de ejecucion de hilos
        self.moving_thread = False
        self.visual_thread = False
        self.mandatory_thread = False

        # Validacion de detencion de movimiento
        self.stop_movement = False

        # Inicializacion de conexion
        try:
            self.ros_client = roslibpy.Ros(
                host = host,
                port = port
            )
            self.ros_client.run()
        except Exception as e:
            raise ValueError(f"Error al intentar la conexion. {e}")

        # Inicializacion de servicios de instancia
        self.set_initial_services()
        # Funcion para carga de ordenes guia del sistema
        self.set_inital_system_orders()

    # Funcion para ejecucion de servicios de movimiento
    def excecute_move_thread(self):
        # Validacion de thread de ejecucion activo
        # print(f"Estado de hilo: {self.moving_thread}")
        if not self.moving_thread:
            self.moving_thread = True
            thread_move = threading.Thread(target = self.execute_move_request)
            thread_move.start()

    # Funcion de ejecucion de servicios de movimiento
    def execute_move_request(self):
        # Variables de preparacion para la ejecucion
        # Función para manejar la respuesta del servicio
        def handle_response_get(response):
            self.serGet_result = response

        def your_callback_function(result):
            print(f"Service call result: {result}")
        # Inicializar el request para el servicio 'get_status'
        # print("INICIO DE HILO")
        request_get = roslibpy.ServiceRequest({
            'change': True
        })
        # Ciclo de ejecucion, mientras la lista solicitudes aun tenga valores
        while self.moviment_list and not self.stop_movement:
            # Ciclo que valida si se esta ejecutando algun servicio
            while True:
                # Primero valor de resultado
                self.serGet_result = None
                sleep(1)
                # print("CICLO CONTINUO")
                # Validar estado actual
                self.services["get_status"]
                self.services['get_status'].call(request_get, handle_response_get)
                # Espera de deteccion de resultado solicitado
                
                while self.serGet_result is None:
                    # print(None)
                    sleep(0.1)
                # Actual estado del robot
                actual_state = self.serGet_result['status']
                
                # Condición para obtener nuevo estado
                if actual_state != "available":
                    continue
                break
            if self.stop_movement:
                break
            # Inicio de ejecucion
            # Obtener la siguiente funcion que se esta ejecutando
            next_move = self.moviment_list.pop(0)
            self.append_service(next_move["service"])
            # Validacion de ejecucion
            try:
                print(f"Calling service {next_move['service']} with args {next_move['args']}")
                # Ejecucion 
                service = self.services.get(next_move['service'])
                # print(service)
                # Validacion final
                if service is not None:
                    # print("hola")
                    request = roslibpy.ServiceRequest(next_move["args"])
                    service.call(request, your_callback_function)
                    # print(f"RESPUESTA DE SERVICIO")
                    # Espera para ejecucion de solicitud
                    sleep(1)
            except Exception as e:
                print(f"Failed to call service with {e}.")
        print("proceso de movimiento terminado")
        self.stop_movement = False
        self.moving_thread = False

    # Funciones para la ejecicion de hilo de oredenes visuales
    def excecute_visual_thread(self):
        # Validacion de thread de ejecucion activo
        if not self.visual_thread:
            self.visual_thread = True
            thread_visual = threading.Thread(target = self.execute_visual_request)
            thread_visual.start()

    def execute_visual_request(self):
        # Ciclo de ejecucion, mientras la lista solicitudes aun tenga valores
        while self.visual_list:
            # Inicio de ejecucion
            # Obtener la siguiente funcion que se esta ejecutando
            next_visual = self.visual_list.pop(0)
            self.append_service(next_visual["service"])
            # Validacion de ejecucion
            try:
                print(f"Calling service {next_visual['service']} with args {next_visual['args']}")
                # Ejecucion 
                service = self.services.get(next_visual['service'])
                # Validacion final
                if service is not None:
                    request = roslibpy.ServiceRequest(next_visual["args"])
                    service.call(request)
                    # Espera para ejecucion de solicitud
                    sleep(1)
            except Exception as e:
                print(f"Failed to call service with {e}.")
        print("proceso visual terminado")
        self.visual_thread = False

    def excecute_mandatory_thread(self):
        # Validacion de thread de ejecucion activo
        if not self.mandatory_thread:
            self.mandatory_thread = True
            thread_mandatory = threading.Thread(target = self.execute_mandatory_request)
            thread_mandatory.start()

    def execute_mandatory_request(self):
        # Ciclo de ejecucion, mientras la lista solicitudes aun tenga valores
        while self.mandatory_list:
            # Inicio de ejecucion
            # Obtener la siguiente funcion que se esta ejecutando
            next_mandatory = self.mandatory_list.pop(0)
            self.append_service(next_mandatory["service"])
            # Validacion de ejecucion
            if next_mandatory["service"] == "stop_movement":
                self.stop_movement = True
                self.moviment_list.clear()
            try:
                print(f"Calling service {next_mandatory['service']} with args {next_mandatory['args']}")
                # Ejecucion 
                service = self.services.get(next_mandatory['service'])
                # Validacion final
                if service is not None:
                    request = roslibpy.ServiceRequest(next_mandatory["args"])
                    service.call(request)
                    # Espera para ejecucion de solicitud
                    sleep(1)
            except Exception as e:
                print(f"Failed to call service with {e}.")
        print("proceso mandatorio terminado")
        self.mandatory_thread = False

    # Funcion para designacion de lista de servicios
    def set_initial_services(self):
        """
        Funcion para asignar los servicios conocidos para la ejecucion de la comunicacion con ros, estos servicios correspoenden a funciones, 
        para validacion de estado del robot, o bien interacciones primarias
        """
        self.services['get_status'] = roslibpy.Service(self.ros_client, '/get_status', self.ros_client.get_service_type('/get_status'))
        self.services['change_status'] = roslibpy.Service(self.ros_client, '/change_status', self.ros_client.get_service_type('/change_status'))
        self.services['stop_all'] = roslibpy.Service(self.ros_client, '/stop_all', self.ros_client.get_service_type('/stop_all'))
        self.services['stop_movement'] = roslibpy.Service(self.ros_client, '/stop_all', self.ros_client.get_service_type('/stop_all'))
        self.services['set_initial_pose'] = roslibpy.Service(self.ros_client, '/set_initial_pose', self.ros_client.get_service_type('/set_initial_pose'))

    def set_inital_system_orders(self):
        print(getcwd())
        with open("./assets/system_orders/system_orders_format.json", "r") as f:
            self.system_task_list = jload(f)
        # print(type(self.system_task_list[0]))

    # Funcion para agregar nuevos servicios si estos no existen en el diccionario actual
    # TODO: Mejorar la logica de la siguiente funcion
    def append_service(self, name_service: str):
        #print(f"nombre de servicio: {name_service}")
        if name_service not in self.services:
            self.services[name_service] = roslibpy.Service(self.ros_client, '/'+name_service, self.ros_client.get_service_type('/'+name_service))
        return 

    # Seccion de funciones para manejo de tareas ejecutadas en la conexion de ros2
    def add_task(self, new_task_list: List, use_movement_system: bool = False):
        cant_move = 0
        cant_visual = 0
        cant_mandatory = 0
        if len(new_task_list) > 0:
            for i, new_task in enumerate(new_task_list):
                if str(new_task["service"]) in MOVECLASS:
                    if not use_movement_system or len(self.system_task_list) <= 0:
                        self.moviment_list.append(new_task)
                    else:
                        print(f"Tareas del sistema: {self.system_task_list}")
                        self.moviment_list.append(self.system_task_list.pop(0))
                    cant_move+=1
                elif str(new_task["service"]) in VISUALCLASS:
                    self.visual_list.append(new_task)
                    cant_visual+=1
                elif str(new_task["service"]) in MANDATORYCLASS and len(self.mandatory_list) <= 0:
                    self.mandatory_list.append(new_task)
                    cant_mandatory+=1
                else:
                    self.message+=f" A tarefa número {i+1} solicitada corresponde a uma tarefa fora das minhas habilidades."
            if cant_visual > 0 or cant_move > 0 or cant_mandatory > 0:
                self.message+=f" As solicitações dadas correspondem a {cant_move} tarefas de movimento, {cant_visual} tarefas visuais e {cant_mandatory} tarefas obrigatórias."                    
            return 
        self.message+=" Não há tarefas para adicionar."
        return

    # Visualizacion de servicios actuales
    def get_actual_task_list(self):
        """ 
        Funcion para visualizar la lista de funciones existentes para interaccion con ros2
        """
        for i, task in enumerate(self.moviment_list):
            print(f"Tarefa de movimento: Tarefa N {i+1}: {task}")
        
        for i, task in enumerate(self.visual_list):
            print(f"Tarefa de visuais: Tarefa N {i+1}: {task}")
        
        for i, task in enumerate(self.mandatory_list):
            print(f"Tarefa de obrigatórias: Tarefa N {i+1}: {task}")

    # Funcion para limpiar el mensaje actual
    def clean_message(self):
        self.message = ""

    # Destructor de clase
    def __del__(self):
        if self.ros_client.is_connected:
            #print("Closing ROS connection")
            self.ros_client.terminate()
        print("Closing ROS connection")