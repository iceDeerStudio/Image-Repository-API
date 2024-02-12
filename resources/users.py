from flask_jwt_extended import jwt_required, get_jwt, current_user
from flask_restx import Resource, Namespace, marshal, reqparse
from models import user_model, users_list_model, message_model
from orm.user import UserORM
from extensions import db

users_namespace = Namespace("users", description="User operations")

users_namespace.add_model("User", user_model)
users_namespace.add_model("UsersList", users_list_model)
users_namespace.add_model("Message", message_model)

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


@users_namespace.route("/<int:user_id>")
@users_namespace.param("user_id", "The user identifier")
class UserResource(Resource):

    @jwt_required()
    @users_namespace.doc(security="Bearer Auth")
    @users_namespace.response(200, "Success", user_model)
    @users_namespace.response(403, "Permission denied", message_model)
    @users_namespace.response(404, "User not found", message_model)
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
    @users_namespace.doc(security="Bearer Auth")
    @users_namespace.response(200, "Success", message_model)
    @users_namespace.response(403, "Permission denied", message_model)
    @users_namespace.response(404, "User not found", message_model)
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
    @users_namespace.doc(security="Bearer Auth")
    @users_namespace.expect(user_parser)
    @users_namespace.response(200, "User updated successfully", message_model)
    @users_namespace.response(403, "Permission denied", message_model)
    @users_namespace.response(404, "User not found", message_model)
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


@users_namespace.route("")
class UserListResource(Resource):

    @jwt_required(optional=True)
    @users_namespace.doc(security="Bearer Auth")
    @users_namespace.expect(user_parser)
    @users_namespace.response(200, "Success", users_list_model)
    @users_namespace.response(400, "Invalid request", message_model)
    @users_namespace.response(403, "Permission denied", message_model)
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
            {"Location": f"/users/{user.id}"},
        )
