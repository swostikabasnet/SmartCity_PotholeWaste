import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from database import db
from api.service.detection_service import detect_image_type
from api.controller.auth.auth_middleware import token_required
from api.models.user_model import User 
from api.models.detection_model import Detection
from api.models.department import Department
from api.models.image import Image
from api.models.tag import Tag
from api.models.relations import DetectionDepartment, DetectionTag
from datetime import datetime

detection_bp = Blueprint('detection_bp', __name__, url_prefix='/detections')


# POST — Detect and Save
@detection_bp.route('/', methods=['POST'])
@token_required
def create_detection(current_user):
    #Upload a detection (pothole or waste) Everything except the image is automatically determined.
    image = request.files.get('image')
    lat = request.form.get('latitude')
    lon = request.form.get('longitude')
    location = request.form.get('location')

    if not image or not lat or not lon or not location:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        latitude = float(lat)
        longitude = float(lon)
    except ValueError:
        return jsonify({'error': 'Invalid latitude/longitude'}), 400

    detection_type, result_data = detect_image_type(image)

    if detection_type is None:
        return jsonify({'message': 'No pothole or waste detected!'}), 200
    
    # # determine  severity/category and department automatically 
    # pothole_severity = result_data.get("pothole_severity") if detection_type == "pothole" else None
    # waste_category = result_data.get("waste_category") if detection_type == "waste" else None
    # department = "Road Department" if detection_type == "pothole" else "Waste Management Department"


    # Determine department and tags
    if detection_type == 'pothole':
        department_name = "Road Department"
        tag_names = [result_data.get('pothole_severity')] 
    else:
        department_name = "Waste Management Department"
        tag_names = [result_data.get('waste_category')] 

    # Find or create department
    department = Department.query.filter_by(name=department_name).first()
    if not department:
        department = Department(name=department_name)
        db.session.add(department)
        db.session.commit()

    # Construct paths for already uploaded images
    image_name = image.filename
    image_path = f"uploads/{detection_type}/{image_name}"
    if detection_type == 'pothole':
        detected_image_path = f"storage/pothole/detected/{image_name}"
    else:
        detected_image_path = f"storage/waste/detected/{image_name}"
   

    # Store in database with user_id
    detection = Detection(
        user_id=current_user.id,
        image_name=result_data['image_name'],
        image_path=image_path,
        detected_image_path=detected_image_path,
        detection_type=detection_type,  # 'pothole' or 'waste'
        latitude=latitude,
        longitude=longitude,
        location=location,
        timestamp=datetime.utcnow(),
        pothole_severity=result_data.get('pothole_severity'),
        waste_category=result_data.get('waste_category'),
        department=result_data.get('department'),
        detection_status=result_data.get('detection_status')    
    )
    db.session.add(detection)
    db.session.commit()

    # Link detection to department
    det_dept = DetectionDepartment(
        detection_id=detection.id,
        department_id=department.id
    )
    db.session.add(det_dept)

    # Link detection to tags
    for t_name in tag_names:
        if t_name:
            tag = Tag.query.filter_by(name=t_name).first()
            if not tag:
                tag = Tag(name=t_name, type=detection_type)
                db.session.add(tag)
                db.session.commit()
            det_tag = DetectionTag(detection_id=detection.id, tag_id=tag.id)
            db.session.add(det_tag)

    # Save uploaded image in Image table
    filename = None
    if image:
        filename = f"{uuid.uuid4().hex}_{image.filename}"
        folder = current_app.config.get('DETECTION_IMAGE_FOLDER')
        if folder:
            path = os.path.join(folder, filename)
            image.save(path)

        img_record = Image(
            id=uuid.uuid4().hex,
            detection_id=detection.id,
            uploaded_filename=filename,
            annotated_filename=None,
            timestamp=str(datetime.utcnow())
        )
        db.session.add(img_record)

    db.session.commit()


    return jsonify({
        'message': f'{detection_type.capitalize()} detected successfully.',
        'data': detection.to_dict()
    }), 201



#  GET — All detections(current user detections only)
@detection_bp.route('/my', methods=['GET'])
@token_required
def get_my_detections(current_user):
    records = Detection.query.filter(Detection.user_id == current_user.id).all()
    # this is feteching dtetctions from db using query
    if not records:
        return jsonify({'message': 'No detections found for this user'}), 200

    return jsonify([r.to_dict() for r in records]), 200

#  GET — All by type(like pthole/waste) for current user
@detection_bp.route('/my/<string:detection_type>', methods=['GET'])
@token_required
def get_my_by_type(current_user, detection_type): # using current_user from the token in the route so it 
    #automatically know the user ID from the token(we  don't need to pass user id in the route)
    if detection_type not in ['pothole', 'waste']:
        return jsonify({'error': 'Invalid detection type'}), 400

    records = Detection.query.filter_by(
        user_id=current_user.id, detection_type=detection_type).all()
    return jsonify([r.to_dict() for r in records]), 200


#  GET — single detection by id of the image for current user

@detection_bp.route('/my/<int:id>', methods=['GET'])
@token_required
def get_my_single(current_user, id):
    record = Detection.query.filter_by(user_id=current_user.id, id=id).first_or_404()
    return jsonify(record.to_dict()), 200


#GET — All detections for current user(uses relationship defined in the user model)
@detection_bp.route('/user', methods=['GET'])
@token_required
def my_detections(current_user):
    return jsonify([d.to_dict(include_user=True) for d in current_user.detections]), 200
#Note: user info ko lagi chai detection model ma to_dict() dunction ma include_user parameter add gareko xa so


# #  GET — All detections by user id (admin can get any user's detections)
# #directly filters detections by user_id
# @detection_bp.route('/user/<int:user_id>', methods=['GET'])
# @token_required
# def get_detections_by_user(current_user, user_id):
#     # Normal users can only access their own detections
#     if current_user.role != 'admin' and current_user.id != user_id:
#         return jsonify({'error': 'Unauthorized access'}), 403

#     detections = Detection.query.filter_by(user_id=user_id).all()
#     if not detections:
#         return jsonify({'message': 'No detections found for this user'}), 404

#     data = []
#     for det in detections:
#         det_dict = det.to_dict()
#         det_dict['user'] = {
#             'id': det.user.id,
#             'email': det.user.email,
#             'role': det.user.role,
#             'organization_name': det.user.organization_name
#         }
#         data.append(det_dict)

#     return jsonify({'detections': data}), 200


# PUT — Update detection (user can update only location)
@detection_bp.route('/my/<int:id>', methods=['PUT'])
@token_required
def update_my_detection(current_user, id):
    data = request.json
    new_location = data.get('location')
    if not new_location:
        return jsonify({'error': 'Location is required'}), 400

    record = Detection.query.filter_by(user_id=current_user.id, id=id).first()
    if not record:
        return jsonify({'error': 'Record not found'}), 404

    record.location = new_location
    db.session.commit()

    return jsonify({'message': f'{record.detection_type.capitalize()} location updated',
                    'data': record.to_dict()}), 200


# DELETE SINGLE — by ID for current user
@detection_bp.route('/my/<int:id>', methods=['DELETE'])
@token_required
def delete_my_detection(current_user, id):
    record = Detection.query.filter_by(user_id=current_user.id, id=id).first()
    if not record:
        return jsonify({'error': 'Record not found'}), 404

    # Remove stored image from disk
    folder = current_app.config.get('DETECTION_IMAGE_FOLDER')
    if folder and record.image_name:
        image_path = os.path.join(folder, record.image_name)
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(record)
    db.session.commit()

    return jsonify({'message': f'{record.detection_type.capitalize()} deleted successfully'}), 200


# DELETE ALL — by type for current user
@detection_bp.route('/my/<string:detection_type>', methods=['DELETE'])
@token_required
def delete_all_my_by_type(current_user, detection_type):
    if detection_type not in ['pothole', 'waste']:
        return jsonify({'error': 'Invalid detection type'}), 400

    records = Detection.query.filter_by(
        user_id=current_user.id, detection_type=detection_type).all()

    folder = current_app.config.get('DETECTION_IMAGE_FOLDER')

    for record in records:
        # Remove stored image from disk
        if folder and record.image_name:
            image_path = os.path.join(folder, record.image_name)
            if os.path.exists(image_path):
                os.remove(image_path)
        db.session.delete(record)

    db.session.commit()

    return jsonify({
        "message": f"All {detection_type} records deleted successfully.",
        "count": len(records)
    }), 200