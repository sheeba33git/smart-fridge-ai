import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

# Ensure uploads folder exists on startup
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
