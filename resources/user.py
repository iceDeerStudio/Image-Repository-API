from flask_restx import Resource, Namespace, marshal, reqparse
from orm.user import UserORM, TokenBlocklistORM
from models import user_model, users_list_model, message_model, token_model
from extensions import db
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt,
    current_user,
)

user_namespace = Namespace("user", description="User operations")

user_namespace.add_model("User", user_model)
user_namespace.add_model("UsersList", users_list_model)
user_namespace.add_model("Message", message_model)
user_namespace.add_model("Token", token_model)

user_parser = reqparse.RequestParser()
user_parser.add_argument(
    "username", type=str, required=True, help="Username of the user."
)
user_parser.add_argument(
    "nickname", type=str, required=True, help="Nickname of the user."
)
user_parser.add_argument(
    "password", type=str, required=False, help="Password of the user."
)
user_parser.add_argument(
    "permission_level",
    type=int,
    required=True,
    help="The permission level of the user (0: visitor, 1: user, 2: admin).",
)

login_parser = reqparse.RequestParser()
login_parser.add_argument(
    "username", type=str, required=True, help="Username of the user."
)
login_parser.add_argument(
    "password", type=str, required=True, help="Password of the user."
)

logout_parser = reqparse.RequestParser()
logout_parser.add_argument(
    "refresh_token", type=str, required=True, help="Refresh token of the user."
)
logout_parser.add_argument(
    "access_token", type=str, required=True, help="Access token of the user."
)


@user_namespace.route("/<int:user_id>")
@user_namespace.param("user_id", "The user identifier")
class UserResource(Resource):

    @jwt_required()
    @user_namespace.doc(security="Bearer Auth")
    @user_namespace.response(200, "Success", user_model)
    @user_namespace.response(403, "Permission denied", message_model)
    @user_namespace.response(404, "User not found", message_model)
    def get(self, user_id):
        """
        Get user by ID
        """
        user = UserORM.query.filter_by(id=user_id).first()
        if not user:
            return marshal({"message": "User not found"}, message_model), 404
        if user_id != current_user.id and current_user.permission_level < 2:
            return marshal({"message": "Permission denied"}, message_model), 403
        return marshal(user.to_dict(), user_model), 200

    @jwt_required()
    @user_namespace.doc(security="Bearer Auth")
    @user_namespace.response(200, "Success", message_model)
    @user_namespace.response(403, "Permission denied", message_model)
    @user_namespace.response(404, "User not found", message_model)
    def delete(self, user_id):
        """
        Delete a user
        """
        user = UserORM.query.filter_by(id=user_id).first()

        if not user:
            return marshal({"message": "User not found"}, message_model), 404
        if current_user.permission_level < max(user.permission_level, 2):
            return (
                marshal(
                    {"message": "You do not have permission to delete this user"},
                    message_model,
                ),
                403,
            )

        db.session.delete(user)
        db.session.commit()
        return marshal({"message": "User deleted successfully"}, message_model), 200

    @jwt_required()
    @user_namespace.doc(security="Bearer Auth")
    @user_namespace.expect(user_parser)
    @user_namespace.response(200, "User updated successfully", message_model)
    @user_namespace.response(403, "Permission denied", message_model)
    @user_namespace.response(404, "User not found", message_model)
    def put(self, user_id):
        """
        Update a user's nickname, password, or permission level
        ---
        Note that a user can only update their own information if they provide a fresh token.
        """
        data = user_parser.parse_args()
        user = UserORM.query.filter_by(id=user_id).first()

        if not user:
            return marshal({"message": "User not found"}, message_model), 404

        if current_user.permission_level < max(user.permission_level, 2):
            if user_id != current_user.id:
                return (
                    marshal(
                        {"message": "You do not have permission to update this user"},
                        message_model,
                    ),
                    403,
                )
            # If the user is updating their own information, they need to provide a fresh token
            if not get_jwt()["fresh"]:
                return (
                    marshal(
                        {
                            "message": "You need to provide a fresh token to update your own information, please log in again"
                        },
                        message_model,
                    ),
                    403,
                )

        if data["permission_level"] > current_user.permission_level:
            return (
                marshal(
                    {
                        "message": "You do not have permission to update a user with that permission level"
                    },
                    message_model,
                ),
                403,
            )

        user.username = data["username"]
        user.nickname = data["nickname"]
        user.permission_level = data["permission_level"]
        if data["password"]:
            user.set_password(data["password"])

        db.session.commit()
        return marshal({"message": "User updated successfully"}, message_model), 200


@user_namespace.route("/")
class UserListResource(Resource):

    @jwt_required(optional=True)
    @user_namespace.doc(security="Bearer Auth")
    @user_namespace.expect(user_parser)
    @user_namespace.response(200, "Success", users_list_model)
    @user_namespace.response(400, "Invalid request", message_model)
    @user_namespace.response(403, "Permission denied", message_model)
    def post(self):
        """
        Create a new user
        """
        data = user_parser.parse_args()

        if not data["password"]:
            return {"message": "password is required"}, 400

        if UserORM.query.filter_by(username=data["username"]).first():
            return {"message": "A user with that username already exists"}, 400

        if data["permission_level"] >= 2:
            if not (
                current_user
                and current_user.permission_level <= data["permission_level"]
            ):
                return {
                    "message": "You do not have permission to create a user with that permission level"
                }, 403

        user = UserORM(
            username=data["username"],
            nickname=data["nickname"],
            permission_level=data["permission_level"],
        )
        user.set_password(data["password"])
        db.session.add(user)

        db.session.commit()
        return (
            marshal({"message": "User created successfully"}, message_model),
            201,
            {"Location": f"/user/{user.id}"},
        )


@user_namespace.route("/login")
class UserLoginResource(Resource):

    @user_namespace.expect(login_parser)
    @user_namespace.response(200, "Success", token_model)
    @user_namespace.response(401, "Invalid credentials", message_model)
    def post(self):
        """
        Log in a user
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


@user_namespace.route("/logout")
class UserLogoutResource(Resource):
    @jwt_required(refresh=True)
    @user_namespace.doc(security="Bearer Auth")
    @user_namespace.response(200, "Success", message_model)
    def post(self):
        """
        Log out a user
        ---
        !!! Requires a refresh token
        This will blacklist the user's refresh token and access token
        """
        jti = get_jwt()["jti"]
        token = TokenBlocklistORM(jti=jti)
        db.session.add(token)
        db.session.commit()
        return marshal({"message": "User logged out"}, message_model), 200


@user_namespace.route("/refresh")
class TokenRefreshResource(Resource):
    @jwt_required(refresh=True)
    @user_namespace.doc(security="Bearer Auth")
    @user_namespace.response(200, "Success", token_model)
    def post(self):
        """
        Refresh a user's access token
        ---
        !!! Requires a refresh token
        This will create a new access token using the user's refresh token
        """
        new_token = create_access_token(identity=current_user, fresh=False)
        return marshal({"access_token": new_token}, token_model), 200
