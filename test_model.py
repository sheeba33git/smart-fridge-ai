from ultralytics import YOLO

# load model
model = YOLO("best.pt")

# give a test image (put any vegetable image in same folder)
results = model("test.jpg")

# print outputs
print("FULL RESULT:", results[0])
print("PROBS:", results[0].probs)