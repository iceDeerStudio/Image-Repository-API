from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from extensions import db

class ImageORM(db.Model):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True)
    description = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hash_value = Column(String(64), nullable=True)
    mimetype = Column(String(64), nullable=True)
    visibility = Column(Integer, default=1)

    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "owner_id": self.owner_id,
            "hash_value": self.hash_value,
            "mimetype": self.mimetype,
            "visibility": self.visibility,
        }