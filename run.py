# Libraries import section
from api import create_app
# Librerias para manipulacion de dbase de datos
from api.utils import ros_conn
from api import db
from api import models
import os

# Creacion de aplicacion siguiendo modulo princial de api - Establecer el contexto de ejecucion de la aplicacion (Desarrollo, prod or test)
app = create_app(config_name = 'development')
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    # Designacion de puerto de trabajo
    port = os.environ.get("PORT", 5000)
    # Ejecucion de aplicacion general
    app.run(debug=True)
    del ros_conn