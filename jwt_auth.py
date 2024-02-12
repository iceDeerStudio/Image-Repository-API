from orm.user import UserORM, TokenBlocklistORM
from flask_jwt_extended import JWTManager

jwt = JWTManager()

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return UserORM.query.filter_by(id=identity).one()


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_data):
    jti = jwt_data["jti"]
    return TokenBlocklistORM.query.filter_by(jti=jti).one_or_none() is not None


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_data):
    return {"message": "The token has expired"}, 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return {"message": f"The token is invalid: {error}"}, 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return {"message": f"Request does not contain an access token: {error}"}, 401


@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_data):
    return {"message": "The token is not fresh, please login again"}, 401


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_data):
    return {"message": "The token has been revoked, please login again"}, 401


@jwt.token_verification_failed_loader
def token_verification_failed_callback(jwt_header, jwt_data):
    return {"message": "The token could not be verified"}, 401


@jwt.user_lookup_error_loader
def user_lookup_error_callback(jwt_header, jwt_data):
    return {"message": f"Error looking up user, please login again"}, 401
