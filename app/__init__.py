from flask import Flask
import logging.config
from .config.logger_config import LOGGING_CONFIG

# Import Blueprints
from .routes.doc_routes import doc_blueprint
from .routes.biometric_routes import biometric_auth_blueprint

from .routes.cheque_routes import cheque_scan_blueprint


def create_app():
    app = Flask(__name__)

    # Configure logging
    logging.config.dictConfig(LOGGING_CONFIG)

    """
    Register Blueprints for modularizing and combining all modules in a single app.
    By this we can also scale and maintain the versions of the app further.
    It can serve all the services with a single host and post with different routes/endpoints.
    All Blueprints are in `routes` dir.
    """
    # Blueprint for documents scanning
    app.register_blueprint(doc_blueprint, url_prefix="/api/doc")

    # Blueprint for biometric authentications
    app.register_blueprint(biometric_auth_blueprint, url_prefix="/api/auth")

    # Blueprint for cheque scanning
    app.register_blueprint(cheque_scan_blueprint, url_prefix="/api/cheque")

    return app
