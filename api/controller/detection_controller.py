import os
from flask import Blueprint, request, jsonify, current_app
from database import db
from api.service.detection_service import detect_image_type
from api.controller.auth.auth_middleware import token_required
from api.models.user_model import User 
from api.models.detection_model import Detection
from datetime import datetime

detection_bp = Blueprint('detection_bp', __name__, url_prefix='/detections')


# POST — Detect and Save
@detection_bp.route('/', methods=['POST'])
@token_required
def detect(current_user):
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

    # Store in database with user_id
    record = Detection(
        user_id=current_user.id,
        image_name=result_data['image_name'],
        detection_type=detection_type,  # 'pothole' or 'waste'
        latitude=latitude,
        longitude=longitude,
        location=location,
        timestamp=datetime.utcnow(),
        severity=result_data.get('severity') if detection_type=='pothole' else None,
        waste_category=result_data.get('waste_category') if detection_type=='waste' else None,
        department='road' if detection_type=='pothole' else 'waste',
        detection_status='pending'    
    )


    db.session.add(record)
    db.session.commit()

    return jsonify({
        'message': f'{detection_type.capitalize()} detected successfully.',
        'data': record.to_dict()
    }), 201



#  GET — All detections(current user detections only)
@detection_bp.route('/my', methods=['GET'])
@token_required
def get_my_detections(current_user):
    records = Detection.query.filter_by(user_id=current_user.id).all()
    return jsonify([r.to_dict() for r in records]), 200


#  GET — All by type(like pthole/waste) for current user
@detection_bp.route('/my/<string:detection_type>', methods=['GET'])
@token_required
def get_my_by_type(current_user, detection_type):
    if detection_type not in ['pothole', 'waste']:
        return jsonify({'error': 'Invalid detection type'}), 400

    records = Detection.query.filter_by(
        user_id=current_user.id, detection_type=detection_type).all()
    return jsonify([r.to_dict() for r in records]), 200


#  GET — Single by type + id for current user

@detection_bp.route('/my/<int:id>', methods=['GET'])
@token_required
def get_my_single(current_user, id):
    record = Detection.query.filter_by(user_id=current_user.id, id=id).first_or_404()
    return jsonify(record.to_dict()), 200


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
    if record.image_name:
        folder = current_app.config.get('DETECTION_IMAGE_FOLDER')
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
    count = len(records)

    folder = current_app.config.get('DETECTION_IMAGE_FOLDER')

    for record in records:
        # Remove stored image from disk
        if record.image_name:
            image_path = os.path.join(folder, record.image_name)
            if os.path.exists(image_path):
                os.remove(image_path)
        db.session.delete(record)

    db.session.commit()

    return jsonify({
        'message': f'All your {detection_type} records deleted',
        'deleted_count': count
    }), 200