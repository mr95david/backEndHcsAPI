# Seccion de importe de librerias
from flask import Flask
from flask_assets import Environment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
# Configuracion general de la api
from api.config import config
from api.setup_security import setup_security_measue_on_aplication

# Database configuration
# Object creation for interactive use of database
db = SQLAlchemy()
migration = Migrate(directory = './api/migrations')

# Security initial config
security = None

# Funcion de creacion de aplicacion
def create_app(config_name: str) -> Flask:
    """
    Function for dynamic create application
    """
    global security

    # Flask api creation
    app = Flask(__name__)
    CORS(app)
    assets = Environment(app)
    # Configuracion general
    app.config.from_object(config[config_name])
    # Config security
    security = setup_security_measue_on_aplication(app)
    # Inicialization of database tool
    db.init_app(app)
    migration.init_app(app, db)

    # Call of routes for user interaction
    from api.routes.index import index
    from api.routes.user_routes import user_bp
    from api.routes.deepgram_routes import deepgram_bp
    from api.routes.openia_routes import openia_bp
    from api.routes.interact_routes import interact_bp
    app.register_blueprint(user_bp)
    app.register_blueprint(index)
    app.register_blueprint(deepgram_bp, url_prefix='/api')
    app.register_blueprint(openia_bp, url_prefix='/api')
    app.register_blueprint(interact_bp, url_prefix='/api')

    return app
