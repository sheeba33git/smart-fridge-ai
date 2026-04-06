# models/vegetable_detector.py
import cv2
from ultralytics import YOLO
import os

# Load YOLOv8 model once (change to your trained model path later)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "yolov8n.pt")
model = YOLO(MODEL_PATH)

def detect_vegetable(image_path):
    """
    Detect the vegetable in the given image.
    Returns: name of detected vegetable or 'Not detected'
    """
    results = model(image_path)
    boxes = results[0].boxes

    if len(boxes) == 0:
        return "No vegetable detected"

    # Take the first prediction
    pred_class_id = int(boxes.cls[0])
    pred_class_name = model.names[pred_class_id]

    return pred_class_name