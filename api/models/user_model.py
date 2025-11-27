from database import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(50), default='user')  # user | organization | admin
    organization_name = db.Column(db.String(150))    # applicable if role is organization

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    #Relationship 
    detections = db.relationship("Detection", backref="user", lazy=True) #friendship = to create relationship between tables

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role,
            "organization_name": self.organization_name,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),

        }
