from database import db
from datetime import datetime
from api.models.image import Image
from api.models.relations import DetectionDepartment, DetectionTag

class Detection(db.Model):
    __tablename__ = "detections"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)  # Who uploaded it
    detection_type = db.Column(db.String(20), nullable=False)  # pothole / waste
    image_name = db.Column(db.String(200), nullable=False)
    image_path = db.Column(db.String(300), nullable=False)  # original uploaded image
    detected_image_path = db.Column(db.String(300), nullable=True) # YOLO output image
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    pothole_severity = db.Column(db.String(20), nullable=True)
    waste_category = db.Column(db.String(50), nullable=True)
    department = db.Column(db.String(100), nullable=False)
    detection_status = db.Column(db.String(50), nullable=False)


    user = db.relationship("User", backref=db.backref("detections", lazy=True))

    # Relationships
    departments = db.relationship("DetectionDepartment",backref="detection",lazy=True,cascade="all, delete-orphan")
    tags = db.relationship("DetectionTag",backref="detection",lazy=True,cascade="all, delete-orphan")
    images = db.relationship("Image",backref="detection",lazy=True,cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "image_name": self.image_name,
            "image_path": self.image_path,              
            "detected_image_path": self.detected_image_path,  
            "detection_type": self.detection_type,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "location": self.location,
            "pothole_severity": self.pothole_severity,
            "waste_category": self.waste_category,
            "department": self.department,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "detection_status": self.detection_status,
            "tags": [t.tag.name for t in self.tags] 
        }
