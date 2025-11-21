from database import db
from datetime import datetime

class Detection(db.Model):
    __tablename__ = "detections"

    id = db.Column(db.Integer, primary_key=True)

    # Who uploaded it
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Common fields
    detection_type = db.Column(db.String(20), nullable=False)  # pothole / waste
    image_name = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
   
    # Pothole-specific
    pothole_severity = db.Column(db.String(20), nullable=True)

    # Waste-specific
    waste_category = db.Column(db.String(50), nullable=True)

    # Department handling the detection
    department = db.Column(db.String(100), nullable=False)

    # # Common status
    detection_status = db.Column(db.String(50), nullable=False)


    user = db.relationship("User", backref=db.backref("detections", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "image_name": self.image_name,
            "detection_type": self.detection_type,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "location": self.location,
            "pothole_severity": self.pothole_severity,
            "waste_category": self.waste_category,
            "department": self.department,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "detection_status": self.detection_status
            
        }
