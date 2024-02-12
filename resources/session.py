from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt, current_user
from flask_restx import Namespace, Resource, reqparse, marshal
from models import token_model, message_model
from orm.user import UserORM, TokenBlocklistORM
from extensions import db

session_namespace = Namespace("session", description="Session operations")
login_parser = reqparse.RequestParser()
login_parser.add_argument(
    "username", type=str, required=True, help="Username of the user."
)
login_parser.add_argument(
    "password", type=str, required=True, help="Password of the user."
)

session_namespace.add_model("Token", token_model)
session_namespace.add_model("Message", message_model)


@session_namespace.route("")
class SessionResource(Resource):

    @session_namespace.expect(login_parser)
    @session_namespace.response(200, "Success", token_model)
    @session_namespace.response(400, "Bad Request", message_model)
    @session_namespace.response(401, "Invalid credentials", message_model)
    @session_namespace.response(500, "Internal Server Error", message_model)
    def post(self):
        """
        Login as a user
        ---
        This will create a new session for a user and return the access and refresh tokens
        """
        data = login_parser.parse_args()
        user = UserORM.query.filter_by(username=data["username"]).first()

        if user and user.check_password(data["password"]):
            access_token = create_access_token(identity=user, fresh=True)
            refresh_token = create_refresh_token(user)
            return (
                marshal(
                    {"access_token": access_token, "refresh_token": refresh_token},
                    token_model,
                ),
                200,
            )

        return marshal({"message": "Invalid credentials"}, message_model), 401
    
    @jwt_required(refresh=True)
    @session_namespace.doc(security="Bearer Auth")
    @session_namespace.response(200, "Success", token_model)
    @session_namespace.response(401, "Unauthorized", message_model)
    @session_namespace.response(500, "Internal Server Error", message_model)
    def get(self):
        """
        Refresh the access token
        ---
        !!! Refresh token required
        This will refresh the access token using the refresh token
        """
        new_token = create_access_token(identity=current_user, fresh=False)
        return marshal({"access_token": new_token}, token_model), 200
    
    @jwt_required(refresh=True)
    @session_namespace.doc(security="Bearer Auth")
    @session_namespace.response(200, "Success", token_model)
    @session_namespace.response(401, "Unauthorized", message_model)
    @session_namespace.response(500, "Internal Server Error", message_model)
    def delete(self):
        """
        Logout a user
        ---
        !!! Refresh token required
        This will blacklist the user's refresh token
        """
        jti = get_jwt()["jti"]
        token = TokenBlocklistORM(jti=jti)
        db.session.add(token)
        db.session.commit()
        return marshal({"message": "User logged out"}, message_model), 200
    