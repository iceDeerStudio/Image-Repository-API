from flask import Flask
from resources.users import users_namespace
from resources.session import session_namespace
from resources.images import images_namespace
from resources.albums import albums_namespace
from resources.util import util_namespace
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
    api.add_namespace(users_namespace)
    api.add_namespace(session_namespace)
    api.add_namespace(images_namespace)
    api.add_namespace(albums_namespace)
    
    # Debug-only routes
    if app.config["DEBUG"]:
        api.add_namespace(util_namespace)
        
    return app