from flask_restx import Model, fields

message_model = Model(
    "Message",
    {"message": fields.String(required=True, description="The message to be returned")},
)

album_model = Model(
    "Album",
    {
        "id": fields.Integer(required=True, description="The album unique identifier"),
        "album_name": fields.String(required=True, description="The name of the album"),
        "description": fields.String(
            required=True, description="The description of the album"
        ),
        "created_at": fields.DateTime(
            required=True, description="The date and time the album was created"
        ),
        "owner_id": fields.Integer(
            required=True, description="The ID of the user who owns the album"
        ),
        "visibility": fields.Integer(
            required=True,
            description="The visibility of the album (0: public, 1: hidden, 2: private)",
        ),
        "images": fields.List(
            fields.Integer, description="List of image IDs in the album"
        ),
    },
)

albums_list_model = Model(
    "AlbumsList",
    {
        "albums": fields.List(
            fields.Nested(album_model), required=True, description="A list of albums"
        )
    },
)

user_model = Model(
    "User",
    {
        "id": fields.Integer(required=True, description="The user unique identifier"),
        "username": fields.String(
            required=True, description="The username of the user"
        ),
        "nickname": fields.String(
            required=True, description="The nickname of the user"
        ),
        "permission_level": fields.Integer(
            required=True,
            description="The permission level of the user (0: visitor, 1: user, 2: admin).",
        ),
    },
)

users_list_model = Model(
    "UsersList",
    {
        "users": fields.List(
            fields.Nested(user_model), required=True, description="A list of users"
        )
    },
)


image_model = Model(
    "Image",
    {
        "id": fields.Integer(required=True, description="The image unique identifier"),
        "description": fields.String(
            required=True, description="The description of the image"
        ),
        "created_at": fields.DateTime(
            required=False, description="The date and time the image was created"
        ),
        "owner_id": fields.Integer(
            required=True, description="The ID of the user who owns the image"
        ),
        "hash_value": fields.String(
            required=False, description="The hash value of the image"
        ),
        "mimetype": fields.String(
            required=False, description="The MIME type of the image"
        ),
        "visibility": fields.Integer(
            required=True,
            description="The visibility of the image (0: public, 1: hidden, 2: private)",
        ),
    },
)


images_list_model = Model(
    "ImagesList",
    {
        "images": fields.List(
            fields.Nested(image_model), required=True, description="A list of images"
        )
    },
)

token_model = Model(
    "Token",
    {
        "access_token": fields.String(
            required=True, description="The access token for the user"
        ),
        "refresh_token": fields.String(
            required=False, description="The refresh token for the user"
        ),
    },
)
