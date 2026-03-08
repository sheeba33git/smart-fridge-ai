import cv2

def detect_vegetable(image_path):

    img = cv2.imread(image_path)

    if img is None:
        return "Unknown"

    height,width,_ = img.shape

    if width > 0:
        return "Tomato"

    return "Unknown"