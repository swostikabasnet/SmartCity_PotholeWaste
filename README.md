# SmartCity Detection(Pothole + Waste)
## YOLO-powered Pothole & Waste Detection System with JWT Authentication
This project merges Pothole Detection and Waste Detection into a single unified API. 
Users upload an image -> YOLO detects pothole/waste -> categorized -> saved in DB.
Every user must login -> token is generated -> all protected routes require token.

## Features
Merged pothole + waste detection in one project
Uses two YOLO models (best.pt & waste.pt)
JWT authentication (login → token → protected routes)
Stores detections in database
Saves original + detected images
Auto pothole severity detection (minor/medium/major)
Auto waste category detection (Glass, Metal, Paper, Plastic, Residual)

## Tech Stack
- Backend: Flask
- DB: PostgreSQL
- ORM: SQLAlchemy
- ML Models: YOLOv8
- Auth: JWT
- Tools: Postman

## API Testing
- Register user -> http://127.0.0.1:5000/auth/register
- Login user -> http://127.0.0.1:5000/auth/login (token is generated)
- Upload image -> http://127.0.0.1:5000/api/detections
- Get all detections of current user -> http://127.0.0.1:5000/api/detections/my
- Get detections by type -> http://127.0.0.1:5000/api/detections/pothole (or waste)
- Get detection by image id -> http://127.0.0.1:5000/api/detections/my/1
- Update loaction -> http://127.0.0.1:5000/api/detections/my/1
- Delete all detections by type -> http://127.0.0.1:5000/api/detections/my/pothole (or waste)
- Delete detection by image id -> http://127.0.0.1:5000/api/detections/my/1



