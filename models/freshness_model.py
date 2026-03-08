import cv2
import numpy as np

def check_freshness(image_path):

    img = cv2.imread(image_path)

    if img is None:
        return "Unknown"

    avg = np.mean(img)

    if avg > 130:
        return "Fresh"
    elif avg > 100:
        return "Medium"
    else:
        return "Spoiled"