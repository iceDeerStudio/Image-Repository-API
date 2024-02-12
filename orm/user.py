from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class UserORM(db.Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    nickname = Column(String(64))
    password_hash = Column(String(192))
    permission_level = Column(Integer, default=1)
    albums = db.relationship("AlbumORM", backref="owner", lazy=True)
    images = db.relationship("ImageORM", backref="owner", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "nickname": self.nickname,
            "permission_level": self.permission_level,
            "albums": [album.id for album in self.albums],
            "images": [image.id for image in self.images],
        }


class TokenBlocklistORM(db.Model):
    __tablename__ = "token_blocklist"
    id = Column(Integer, primary_key=True)
    jti = Column(String(36), nullable=False)
    created_at = Column(DateTime, server_default=func.now())