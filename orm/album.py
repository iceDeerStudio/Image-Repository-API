from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from extensions import db

class AlbumORM(db.Model):
    __tablename__ = "albums"
    id = Column(Integer, primary_key=True)
    album_name = Column(String(64), nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    visibility = Column(Integer, default=1)
    images = db.relationship(
        "ImageORM",
        secondary="album_images",
        lazy="subquery",
        backref=db.backref("albums", lazy=True),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "owner_id": self.owner_id,
            "visibility": self.visibility,
            "images": [image.id for image in self.images],
        }


class AlbumImagesORM(db.Model):
    __tablename__ = "album_images"
    album_id = Column(Integer, ForeignKey("albums.id"), primary_key=True)
    image_id = Column(Integer, ForeignKey("images.id"), primary_key=True)