import os
import time
from flask import current_app
from ultralytics import YOLO

# Load models once
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POTHOLE_MODEL_PATH = os.path.join(BASE_DIR, '..', 'models', 'best.pt')
WASTE_MODEL_PATH = os.path.join(BASE_DIR, '..', 'models', 'waste.pt')

try:
    POTHOLE_MODEL = YOLO(POTHOLE_MODEL_PATH)
    WASTE_MODEL = YOLO(WASTE_MODEL_PATH)
except Exception as e:
    print("Error loading YOLO models:", e)
    POTHOLE_MODEL = None
    WASTE_MODEL = None


def detect_image_type(image): #Detect pothole or waste and save images to the correct storage folders."""

    if not POTHOLE_MODEL or not WASTE_MODEL:
        return None, None

    timestamp = int(time.time())
    original_filename = f"{timestamp}_{image.filename}"
    detected_filename = f"{timestamp}_detected_{image.filename}"

    #  Saving the  ORIGINAL images
    pothole_original_path = os.path.join(current_app.config['POTHOLE_ORIGINAL_FOLDER'], original_filename)
    waste_original_path = os.path.join(current_app.config['WASTE_ORIGINAL_FOLDER'], original_filename)

    # Save one temporary copy to run detection
    temp_path = os.path.join(current_app.config['STORAGE_FOLDER'], f"temp_{original_filename}")
    image.save(temp_path)

    # -----------------Run POTHOLE detection------------------
    pothole_results = POTHOLE_MODEL.predict(source=temp_path, save=False, conf=0.5)

    if len(pothole_results[0].boxes) > 0:
        # Save original inside pothole/original
        image.save(pothole_original_path)

        # Save detected inside pothole/detected
        pothole_detected_path = os.path.join(current_app.config['POTHOLE_DETECTED_FOLDER'], detected_filename)
        pothole_results[0].save(filename=pothole_detected_path)

        os.remove(temp_path)
        return "pothole", {
            "image_name": original_filename,
            "detected_image_path": pothole_detected_path,
            "status": "Pothole detected"
        }

    # ------------------ Run WASTE detection ------------------
    waste_results = WASTE_MODEL.predict(source=temp_path, save=False, conf=0.5)

    if len(waste_results[0].boxes) > 0:
        # Save original inside waste/original
        image.save(waste_original_path)

        # Save detected inside waste/detected
        waste_detected_path = os.path.join(current_app.config['WASTE_DETECTED_FOLDER'], detected_filename)
        waste_results[0].save(filename=waste_detected_path)

        first_class = int(waste_results[0].boxes.cls[0].item())
        CLASS_MAP = {0: 'Glass', 1: 'Metal', 2: 'Paper', 3: 'Plastic', 4: 'Residual'}
        category = CLASS_MAP.get(first_class, "Unknown")

        os.remove(temp_path)
        return "waste", {
            "image_name": original_filename,
            "detected_image_path": waste_detected_path,
            "detection_status": f"{category} detected",
            "is_waste": True,
            "waste_category": category,
            "is_recyclable": category not in ["Residual"],
            "is_decomposable": category == "Paper"
        }

    # No detection = delete temp file
    os.remove(temp_path)
    return None, None
