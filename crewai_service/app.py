from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from analysis import analyze_text

load_dotenv()

app = Flask(__name__)
CORS(app)

# Health check route
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

# Placeholder analyze route (CrewAI will go here later)
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")

    if not text.strip():
        return jsonify({"error": "text is required"}), 400

    result = analyze_text(text)
    return jsonify({"analysis": result})

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6001, debug=True)
