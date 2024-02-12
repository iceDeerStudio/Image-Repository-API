from flask_restx import Resource, Namespace, marshal, reqparse
from werkzeug.datastructures import FileStorage
from flask_jwt_extended import jwt_required, current_user
from flask import send_file, current_app, request
from models import image_model, images_list_model, message_model
from orm.image import ImageORM
from extensions import db
from sqlalchemy import or_
import hashlib
import os

image_namespace = Namespace("image", description="Image operations")

image_namespace.add_model("Image", image_model)
image_namespace.add_model("ImagesList", images_list_model)
image_namespace.add_model("Message", message_model)

image_parser = reqparse.RequestParser()
image_parser.add_argument(
    "description",
    type=str,
    required=True,
    help="Description of the image",
)
image_parser.add_argument(
    "visibility",
    type=int,
    required=True,
    help="Visibility of the image (0: public, 1: hidden, 2: private)",
)

file_parser = image_namespace.parser()
file_parser.add_argument(
    "file", location="files", type=FileStorage, required=True, help="Image file"
)


@image_namespace.route("/<int:image_id>")
@image_namespace.param("image_id", "The image identifier")
class ImageResource(Resource):

    @jwt_required(optional=True)
    @image_namespace.doc(security="Bearer Auth")
    @image_namespace.response(200, "Success", image_model)
    @image_namespace.response(403, "Permission denied", message_model)
    @image_namespace.response(404, "Image not found", message_model)
    def get(self, image_id):
        """
        Get image by ID.
        """
        image = ImageORM.query.get(image_id)

        if not image:
            return marshal({"message": "Image not found"}, message_model), 404
        if image.visibility == 1 and not current_user:
            return marshal({"message": "Permission denied"}, message_model), 403
        if image.visibility == 2 and (
            not current_user or image.owner_id != current_user.id
        ):
            return marshal({"message": "Permission denied"}, message_model), 403

        return marshal(image.to_dict(), image_model), 200

    @jwt_required()
    @image_namespace.doc(security="Bearer Auth")
    @image_namespace.expect(image_parser)
    @image_namespace.response(201, "Image created successfully", message_model)
    @image_namespace.response(403, "Permission denied", message_model)
    def put(self, image_id):
        """
        Update image by ID.
        """
        data = image_parser.parse_args()
        image = ImageORM.query.get(image_id)

        if not image:
            return marshal({"message": "Image not found"}, message_model), 404
        if image.owner_id != current_user.id and current_user.permission_level < 2:
            return marshal({"message": "Permission denied"}, message_model), 403

        image.description = data["description"]
        image.visibility = data["visibility"]
        db.session.commit()

        return marshal({"message": "Image updated successfully"}, message_model), 200

    @jwt_required()
    @image_namespace.doc(security="Bearer Auth")
    @image_namespace.response(200, "Image deleted", message_model)
    @image_namespace.response(403, "Permission denied", message_model)
    @image_namespace.response(404, "Image not found", message_model)
    def delete(self, image_id):
        """
        Delete image by ID.
        """
        image = ImageORM.query.get(image_id)
        if not image:
            return marshal({"message": "Image not found"}, message_model), 404
        if image.owner_id != current_user.id and current_user.permission_level < 2:
            return marshal({"message": "Permission denied"}, message_model), 403
        db.session.delete(image)
        db.session.commit()
        return marshal({"message": "Image deleted"}, message_model), 200


@image_namespace.route("/")
class ImageListResource(Resource):
    @jwt_required(optional=True)
    @image_namespace.doc(security="Bearer Auth")
    @image_namespace.response(200, "Success", images_list_model)
    def get(self):
        """
        Return a list of images.
        """
        if current_user:
            images = ImageORM.query.filter(
                or_(
                    ImageORM.visibility == 0,
                    ImageORM.owner_id == current_user.id,
                    current_user.permission_level >= 2,
                )
            ).all()
        else:
            images = ImageORM.query.filter(ImageORM.visibility == 0).all()
        return (
            marshal(
                {"images": [image.to_dict() for image in images]}, images_list_model
            ),
            200,
        )

    @jwt_required()
    @image_namespace.doc(security="Bearer Auth")
    @image_namespace.expect(image_parser)
    @image_namespace.response(201, "Image created successfully", message_model)
    @image_namespace.response(403, "Permission denied", message_model)
    def post(self):
        """
        Create a new image.
        """
        data = image_parser.parse_args()
        if current_user.permission_level < 1:
            return marshal({"message": "Permission denied"}, message_model), 403
        image = ImageORM(
            description=data["description"] if data["description"] else "",
            owner_id=current_user.id,
            hash_value=None,
            mimetype=None,
            visibility=data["visibility"] if data["visibility"] is not None else 1,
        )
        db.session.add(image)
        current_user.images.append(image)
        db.session.commit()
        return (
            marshal({"message": "Image created successfully"}, message_model),
            201,
            {"Location": f"/image/{image.id}"},
        )


@image_namespace.route("/file/<int:image_id>")
class ImageFileResource(Resource):
    @jwt_required(optional=True)
    @image_namespace.doc(security="Bearer Auth")
    @image_namespace.response(200, "Success")
    @image_namespace.response(403, "Permission denied", message_model)
    @image_namespace.response(404, "Image not found or file not found", message_model)
    def get(self, image_id):
        """
        Return the image file.
        ---
        Retrieves an image file by its ID. This endpoint directly streams the binary content of the image file.
        """
        image = ImageORM.query.get(image_id)

        if not image:
            return {"message": "Image not found"}, 404
        if image.visibility == 1 and not current_user:
            return {"message": "Permission denied"}, 403
        if image.visibility == 2 and (
            not current_user or image.owner_id != current_user.id
        ):
            return {"message": "Permission denied"}, 403
        if not image.hash_value:
            return {"message": "Image file not found"}, 404

        return send_file(
            os.path.join(current_app.config["STORAGE_PATH"], image.hash_value),
            mimetype=image.mimetype,
        )

    @jwt_required()
    @image_namespace.doc(security="Bearer Auth")
    @image_namespace.expect(file_parser)
    @image_namespace.response(201, "Image uploaded", message_model)
    @image_namespace.response(403, "Permission denied", message_model)
    @image_namespace.response(404, "Image not found", message_model)
    def post(self, image_id):
        """
        Upload an image file.
        """
        image = ImageORM.query.get(image_id)

        if not image:
            return marshal({"message": "Image not found"}, message_model), 404
        if image.owner_id != current_user.id and current_user.permission_level < 2:
            return marshal({"message": "Permission denied"}, message_model), 403

        image_file = request.files["file"]
        file_hash = hashlib.sha256(image_file.read()).hexdigest()
        file_path = os.path.join(current_app.config["STORAGE_PATH"], file_hash)
        if not os.path.exists(file_path):
            image_file.seek(0)
            image_file.save(file_path)
        image.mimetype = image_file.mimetype
        image.hash_value = file_hash

        db.session.commit()
        return marshal({"message": "Image uploaded"}, message_model), 200
