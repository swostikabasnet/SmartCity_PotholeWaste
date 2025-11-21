from flask import Flask
from flask_cors import CORS
from database import db, migrate
from api.controller.detection_controller import detection_bp
import os
from config import Config
from api.controller.auth.auth_controller import auth_bp
from api.models.detection_model import Detection



def create_app():
    app = Flask(__name__)
    CORS(app)

    # Load configuration form Congig class
    app.config.from_object(Config)
    
    #initializing db and migrations
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprint
    app.register_blueprint(detection_bp, url_prefix='/api/detections')
    app.register_blueprint(auth_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
