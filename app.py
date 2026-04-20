from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import sys
from datetime import datetime
from werkzeug.utils import secure_filename
import sqlite3
import logging
import numpy as np

from config import UPLOAD_FOLDER
from database import create_tables, insert_data, get_all, update_quantity
from ultralytics import YOLO

# ---------------- LOGGING ----------------
logging.basicConfig(level=logging.INFO)

# ---------------- PATH FIX ----------------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ---------------- MODEL PATH ----------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

if getattr(sys, 'frozen', False):
    MODEL_PATH = os.path.join(os.path.dirname(sys.executable), "best.pt")
else:
    MODEL_PATH = os.path.join(BASE_DIR, "best.pt")

# ---------------- MODEL ----------------
model = None

def get_model():
    global model
    if model is None:
        try:
            print("📦 Loading model from:", MODEL_PATH)

            if not os.path.exists(MODEL_PATH):
                print("❌ best.pt NOT FOUND")
                return None

            model = YOLO(MODEL_PATH)

            print("✅ MODEL LOADED")
            print("📊 Classes:", model.names)

        except Exception as e:
            print("❌ MODEL LOAD ERROR:", e)
            model = None

    return model

# ---------------- FLASK ----------------
app = Flask(
    __name__,
    template_folder=resource_path("templates"),
    static_folder=resource_path("static")
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

create_tables()

# ---------------- AI ----------------
def detect_vegetable(path):
    try:
        model = get_model()

        if model is None:
            print("❌ Model not loaded")
            return "Unknown"

        results = model(path)

        if not results:
            print("❌ No results")
            return "Unknown"

        result = results[0]
        probs = getattr(result, "probs", None)

        if probs is None:
            print("❌ No probs attribute in result")
            return "Unknown"

        # ✅ FIXED: Normalize tensor → CPU → numpy → flat array
        # Works on ALL environments: local, Render, CPU-only, GPU
        data = probs.data
        if hasattr(data, "cpu"):
            data = data.cpu()
        if hasattr(data, "numpy"):
            data = data.numpy()

        data = np.array(data).flatten()

        class_id = int(np.argmax(data))
        confidence = float(data[class_id])

        if confidence < 0.4:
            print(f"⚠️ Low confidence ({confidence:.2f}), returning Unknown")
            return "Unknown"

        label = model.names[class_id]
        print(f"✅ Detected: {label} (confidence: {confidence:.2f})")
        return label

    except Exception as e:
        print(f"❌ detect_vegetable ERROR: {e}")
        return "Unknown"

# ---------------- PROCESS ----------------
def process_class(label):
    label = label.lower()

    # ✅ FIXED: Model outputs "Rotten", not "Spoiled" — check prefix correctly
    fresh = "Fresh" if label.startswith("fresh") else "Spoiled"

    if "tomato" in label:
        return "Tomato", fresh
    elif "potato" in label:
        return "Potato", fresh
    elif "cabbage" in label:
        return "Cabbage", fresh
    elif "brinjal" in label or "brijal" in label:
        return "Brinjal", fresh
    elif "carrot" in label:
        return "Carrot", fresh
    elif "banana" in label:
        return "Banana", fresh
    elif "apple" in label:
        return "Apple", fresh

    print("⚠️ UNKNOWN LABEL:", label)
    return "Unknown", "Fresh"

# ---------------- EXPIRY ----------------
def predict_expiry(veg, fresh):
    if fresh == "Spoiled":
        return 0
    return 5

# ---------------- STOCK ----------------
def calculate_stock(data):
    stock = {}

    for item in data:
        veg = item[1]
        qty = item[6]

        if veg not in stock:
            stock[veg] = 0

        stock[veg] += qty

    return stock

# ---------------- ROUTES ----------------
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/")
def dashboard():
    data = get_all()

    total = len(data)
    fresh = len([d for d in data if d[2] == "Fresh"])
    spoiled = len([d for d in data if d[2] == "Spoiled"])

    stock = calculate_stock(data)

    low_stock = [veg for veg, qty in stock.items() if qty < 1]
    spoiled_items = [d for d in data if d[2] == "Spoiled"]

    return render_template(
        "dashboard.html",
        data=data,
        total=total,
        fresh=fresh,
        spoiled=spoiled,
        stock=stock,
        low_stock=low_stock,
        spoiled_items=spoiled_items
    )

@app.route("/history")
def history():
    data = get_all()
    return render_template("history.html", data=data)

@app.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files["image"]
        quantity = float(request.form.get("quantity", 1))

        filename = secure_filename(file.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(path)

        label = detect_vegetable(path)
        print("🔥 RAW LABEL:", label)

        veg, fresh = process_class(label)
        expiry = predict_expiry(veg, fresh)

        insert_data(
            veg,
            fresh,
            expiry,
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            filename,
            quantity
        )

        return redirect(url_for("dashboard"))

    except Exception as e:
        print("❌ UPLOAD ERROR:", e)
        return "Error occurred. Check logs."

@app.route("/remove", methods=["POST"])
def remove():
    veg = request.form.get("veg")
    quantity = float(request.form.get("quantity"))

    update_quantity(veg, quantity)
    return redirect(url_for("dashboard"))

@app.route("/clear", methods=["POST"])
def clear():
    conn = sqlite3.connect("fridge.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fridge")
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Running on port {port}")
    app.run(host="0.0.0.0", port=port)