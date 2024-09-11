# Libraries import
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


# Function for security config
def setup_security_measue_on_aplication(app):
    """
    This function sets up the security measure on the flask application

    :param app: The flask app that needs to be protected
    :return: all the protection measure applied on the app
    """
    limiter = Limiter(
        get_remote_address,
        app = app,
        default_limits = app.config['RATE_LIMITER_OPTS']
    )

    return {"limiter": limiter}