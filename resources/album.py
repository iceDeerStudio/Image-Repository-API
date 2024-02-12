from flask_restx import Namespace, Resource, reqparse, marshal
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user
from models import album_model, albums_list_model, message_model
from orm.album import AlbumORM
from orm.image import ImageORM
from extensions import db
from sqlalchemy import or_

album_namespace = Namespace("album", description="Album operations")

album_namespace.add_model("Album", album_model)
album_namespace.add_model("AlbumsList", albums_list_model)
album_namespace.add_model("Message", message_model)

album_parser = reqparse.RequestParser()
album_parser.add_argument(
    "album_name", type=str, required=True, help="Name of the album."
)
album_parser.add_argument(
    "description", type=str, required=True, help="Description of the album."
)
album_parser.add_argument(
    "visibility",
    type=int,
    required=True,
    help="Visibility of the album (0: public, 1: hidden, 2: private).",
)
album_parser.add_argument(
    "images",
    type=int,
    required=True,
    action="append",
    help="List of image IDs to include in the album.",
)


@album_namespace.route("/<int:album_id>")
@album_namespace.param("album_id", "The album identifier")
class AlbumResource(Resource):

    @jwt_required(optional=True)
    @album_namespace.doc(security="Bearer Auth")
    @album_namespace.response(200, "Success", album_model)
    @album_namespace.response(403, "Permission denied", message_model)
    @album_namespace.response(404, "Album not found", message_model)
    def get(self, album_id):
        """
        Get album by ID.
        """
        album = AlbumORM.query.filter_by(id=album_id).first()
        if not album:
            return marshal({"message": "Album not found"}, message_model), 404
        if album.visibility == 1 and not current_user:
            return marshal({"message": "Permission denied"}, message_model), 403
        if album.visibility == 2 and (
            not current_user or album.owner_id != current_user.id
        ):
            return marshal({"message": "Permission denied"}, message_model), 403
        return marshal(album.to_dict(), album_model), 200

    @jwt_required()
    @album_namespace.doc(security="Bearer Auth")
    @album_namespace.expect(album_parser)
    @album_namespace.response(200, "Album updated successfully", message_model)
    @album_namespace.response(404, "Album not found", message_model)
    @album_namespace.response(403, "Permission denied", message_model)
    def put(self, album_id):
        """
        Update album by ID.
        """
        data = album_parser.parse_args()
        album = AlbumORM.query.filter_by(id=album_id).first()

        if not album:
            return marshal({"message": "Album not found"}, message_model), 404
        if album.owner_id != current_user.id and current_user.permission_level < 2:
            return marshal({"message": "Permission denied"}, message_model), 403

        album.album_name = data["album_name"] if data["album_name"] else "Untitled"
        album.description = data["description"]
        album.visibility = data["visibility"]
        album.images = [
            ImageORM.query.get(id) for id in data["images"] if ImageORM.query.get(id)
        ]

        db.session.commit()
        return marshal({"message": "Album updated successfully"}, message_model), 200

    @jwt_required()
    @album_namespace.doc(security="Bearer Auth")
    @album_namespace.response(200, "Album deleted successfully", message_model)
    @album_namespace.response(404, "Album not found", message_model)
    @album_namespace.response(403, "Permission denied", message_model)
    def delete(self, album_id):
        """
        Delete album by ID.
        """
        album = AlbumORM.query.filter_by(id=album_id).first()

        if not album:
            return marshal({"message": "Album not found"}, message_model), 404
        if album.owner_id != current_user.id and current_user.permission_level < 2:
            return marshal({"message": "Permission denied"}, message_model), 403

        db.session.delete(album)

        db.session.commit()
        return marshal({"message": "Album deleted successfully"}, message_model), 200


@album_namespace.route("/")
class AlbumListResource(Resource):
    @jwt_required(optional=True)
    @album_namespace.doc(security="Bearer Auth")
    @album_namespace.response(200, "Success", albums_list_model)
    def get(self):
        """
        Get list of albums.
        """
        if current_user:
            albums = AlbumORM.query.filter(
                or_(
                    AlbumORM.visibility == 0,
                    AlbumORM.owner_id == current_user.id,
                    current_user.permission_level >= 2,
                )
            ).all()
        else:
            albums = AlbumORM.query.filter(AlbumORM.visibility == 0).all()

        return (
            marshal(
                {"albums": [album.to_dict() for album in albums]}, albums_list_model
            ),
            200,
        )

    @jwt_required()
    @album_namespace.doc(security="Bearer Auth")
    @album_namespace.expect(album_parser)
    @album_namespace.response(201, "Album created successfully", message_model)
    @album_namespace.response(403, "Permission denied", message_model)
    def post(self):
        """
        Create a new album.
        """
        data = album_parser.parse_args()

        if not current_user.permission_level > 0:
            return marshal({"message": "Permission denied"}, message_model), 403

        album = AlbumORM(
            album_name=data["album_name"] if data["album_name"] else "Untitled",
            description=data["description"],
            visibility=data["visibility"],
            owner_id=current_user.id,
        )
        album.images = [
            ImageORM.query.get(id) for id in data["images"] if ImageORM.query.get(id)
        ]
        db.session.add(album)
        current_user.albums.append(album)

        db.session.commit()
        return (
            marshal({"message": "Album created successfully"}, message_model),
            201,
            {"Location": f"/album/{album.id}"},
        )
