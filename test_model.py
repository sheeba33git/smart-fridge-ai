from ultralytics import YOLO

# Load model
model = YOLO("best.pt")

# Test image
results = model.predict("test.jpg", show=True)

for r in results:
    probs = r.probs
    if probs:
        class_id = probs.top1
        print("Prediction:", model.names[class_id])