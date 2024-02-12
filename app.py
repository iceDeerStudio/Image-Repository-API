from flask import Flask
from resources.user import user_namespace
from resources.image import image_namespace
from resources.album import album_namespace
from resources.utils import utils_namespace
from extensions import db, api
from jwt_auth import jwt

def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object("config.Config")

    # Initialize SQLAlchemy
    db.init_app(app)

    # Initialize JWT
    jwt.init_app(app)

    # Initialize Flask-RESTX
    api.init_app(app)

    # Add resources
    api.add_namespace(user_namespace)
    api.add_namespace(image_namespace)
    api.add_namespace(album_namespace)
    
    # Debug-only routes
    if app.config["DEBUG"]:
        api.add_namespace(utils_namespace)
        
    return app