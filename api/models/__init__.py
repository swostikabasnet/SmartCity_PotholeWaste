from .user_model import User
from .detection_model import Detection
from .department import Department
from .image import Image
from .tag import Tag
from .relations import DetectionDepartment, DetectionTag
from database import db

# creating a helper list of all models
all_models = [User, Detection, Department, Image, Tag, DetectionDepartment, DetectionTag]
