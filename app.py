from flask import Flask, render_template, request
import os
from datetime import datetime
from werkzeug.utils import secure_filename

from config import UPLOAD_FOLDER
from database import create_tables, insert_data, get_all

# ---------------- AI MODULES ----------------

try:
    from models.vegetable_detector import detect_vegetable
    from models.freshness_model import check_freshness
    from models.expiry_predictor import predict_expiry
except:
    # fallback AI functions
    def detect_vegetable(path):
        return "Tomato"

    def check_freshness(path):
        return "Fresh"

    def predict_expiry(veg, fresh):
        if fresh == "Fresh":
            return "3 Days"
        return "0 Day"

# ---------------- NOTIFICATION MODULE ----------------

try:
    from notifications.mobile_alert import send_mobile_alert
except:
    def send_mobile_alert(msg):
        print("Mobile Alert:", msg)

# ---------------- FLASK APP ----------------

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Create DB tables
create_tables()

# ---------------- DASHBOARD ----------------

@app.route("/")
def dashboard():

    data = get_all()

    total = len(data)
    fresh = len([d for d in data if d[2] == "Fresh"])
    spoiled = len([d for d in data if d[2] == "Spoiled"])

    return render_template(
        "dashboard.html",
        data=data,
        total=total,
        fresh=fresh,
        spoiled=spoiled,
        result=None
    )

# ---------------- IMAGE UPLOAD ----------------

@app.route("/upload", methods=["POST"])
def upload():

    if "image" not in request.files:
        return "No file uploaded"

    file = request.files["image"]

    if file.filename == "":
        return "No selected file"

    filename = secure_filename(file.filename)

    # 🔹 Ensure folder exists again before saving
    upload_folder = app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    path = os.path.join(upload_folder, filename)

    file.save(path)

    # -------- AI Processing --------

    veg = detect_vegetable(path)
    fresh = check_freshness(path)
    expiry = predict_expiry(veg, fresh)

    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    insert_data(veg, fresh, expiry, date)

    # -------- Mobile Notification --------

    if fresh == "Spoiled":
        send_mobile_alert(f"{veg} is spoiled in refrigerator")

    # -------- Dashboard Data --------

    data = get_all()

    total = len(data)
    fresh_count = len([d for d in data if d[2] == "Fresh"])
    spoiled = len([d for d in data if d[2] == "Spoiled"])

    result = {
        "veg": veg,
        "fresh": fresh,
        "expiry": expiry,
        "image": filename
    }

    return render_template(
        "dashboard.html",
        data=data,
        total=total,
        fresh=fresh_count,
        spoiled=spoiled,
        result=result
    )

# ---------------- HISTORY PAGE ----------------

@app.route("/history")
def history():

    data = get_all()

    return render_template("history.html", data=data)

# ---------------- RUN APP ----------------

if __name__ == "__main__":
    app.run(debug=True)