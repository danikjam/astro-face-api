from flask import Flask, request, jsonify
from deepface import DeepFace
import tempfile
import os

app = Flask(__name__)

@app.route("/analyze_faces", methods=["POST"])
def analyze_faces():
    if 'image1' not in request.files or 'image2' not in request.files:
        return jsonify({"error": "Недостаточно изображений"}), 400

    image1 = request.files['image1']
    image2 = request.files['image2']

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f1,          tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f2:
        f1.write(image1.read())
        f2.write(image2.read())
        f1_path, f2_path = f1.name, f2.name

    try:
        result = DeepFace.verify(f1_path, f2_path, enforce_detection=False)
        similarity = result['distance']
        score = max(0, int((1 - similarity) * 100))
        compatibility = min(score + 10, 100)
        os.remove(f1_path)
        os.remove(f2_path)
        return jsonify({"face_compatibility": compatibility})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)