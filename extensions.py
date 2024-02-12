from flask_sqlalchemy import SQLAlchemy
from flask_restx import Resource, Api, marshal
from models import message_model

db = SQLAlchemy()

api = Api(
    version="1.0",
    title="Image Repository API",
    description="A simple Image Repository API",
    security="Bearer Auth",
    authorizations={
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "JWT Token",
        }
    },
    doc="/docs/",
)

@api.route("/health")
class HealthCheck(Resource):
    @api.response(200, "Success", message_model)
    def get(self):
        """
        Health check.
        """
        return marshal({"message": "Service is healthy"}, message_model), 200
    
@api.route("/version")
class Version(Resource):
    @api.response(200, "Success", message_model)
    def get(self):
        """
        Get version.
        """
        return marshal({"message": api.version}, message_model), 200