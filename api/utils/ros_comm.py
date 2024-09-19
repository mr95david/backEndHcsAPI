# 3 Seccion de importe de librerias
from typing import Dict
import roslibpy
from time import sleep

# Clase para conexion con cliente de ros y ejecucion de servicios
class RosClientManager:
    def __init__(self, host:str = "127.0.0.1", port:int = 9090):
        # Inicializar cliente ROS
        self.ros_client = roslibpy.Ros(
            host=host,
            port=port
        )
        self.ros_client.run()

        # Inicializar los servicios comunes
        self.services = {
            'get_status': roslibpy.Service(
                self.ros_client, '/get_status', self.ros_client.get_service_type('/get_status')),
            'change_status': roslibpy.Service(
                self.ros_client, '/change_status', self.ros_client.get_service_type('/change_status')),
            'stop_all': roslibpy.Service(
                self.ros_client, '/stop_all', self.ros_client.get_service_type('/stop_all')),
            'set_initial_pose': roslibpy.Service(
                self.ros_client, '/set_initial_pose', self.ros_client.get_service_type('/set_initial_pose'))
        }

        self.serGet_result = None

    def sendTask(self, api_calls):
        # Función para manejar la respuesta del servicio
        def handle_response_get(response):
            self.serGet_result = response

        # Inicializar el request para el servicio 'get_status'
        request_get = roslibpy.ServiceRequest({
            'change': True
        })

        # Local services
        local_services = {}

        # Llamar al servicio 'get_status'
        self.services['get_status'].call(request_get, handle_response_get)

        # Esperar a que se obtenga un resultado
        while self.serGet_result is None:
            sleep(0.1)

        actual_state = self.serGet_result['status']

        for call in api_calls:
            # Ciclo de validación de estado de robot
            while True:
                self.serGet_result = None
                sleep(1)

                # Validar estado actual
                self.services['get_status'].call(request_get, handle_response_get)

                while self.serGet_result is None:
                    sleep(0.1)

                actual_state = self.serGet_result['status']

                # Condición para obtener nuevo estado
                if actual_state != "available":
                    continue

                break

            local_services = self.append_service(
                call["service"],
                local_services
            )

            # Llamada de servicio para la tarea actual
            try:
                print(f"Calling service {call['service']} with args {call['args']}")
                service = local_services.get(call['service']) #self.services.get(call['service'])
                if service is not None:
                    request = roslibpy.ServiceRequest(call["args"])
                    service.call(request)
                    sleep(1)
                else:
                    print(f"Service {call['service']} not found.")

            except Exception as e:
                print(f"Failed to call service with {e}.")

    # Metodo para agregar nuevo servicio
    def append_service(
        self, name: str, services: Dict[str, roslibpy.Service]
    ) -> Dict[str, roslibpy.Service]:
        if name not in services:
            services[name] = roslibpy.Service(self.ros_client, name, self.ros_client.get_service_type(name))
        return services

    # Destructor para cerrar la conexión con el cliente ROS
    def __del__(self):
        if self.ros_client.is_connected:
            print("Closing ROS connection")
            self.ros_client.terminate()

def getInitialPose(
    # Se utilizan los valores por defecto donde se incia el experimento para cada una de las pruebas
    x:float = -0.00690361,
    y:float = 0.13486863,
    z_or:float = 0.0003687,
    w_or:float = 0.99999
) -> dict:
    # Definicion de ojeto de interaccion con servicio de designacion de pose inicial
    pose_order = {
    'header': {
        'stamp': {
            'secs': 0,
            'nsecs': 0
        },
        'frame_id': 'map'
    },
    'pose': {
        'pose': {
            'position': {
                'x': x,
                'y': y,
                'z': 0.0
            },
            'orientation': {
                'x': 0.0,
                'y': 0.0,
                'z': z_or,
                'w': w_or
            }
        },
        'covariance': [0.0] * 36  # Covarianza por defecto
    }
}
    return pose_order