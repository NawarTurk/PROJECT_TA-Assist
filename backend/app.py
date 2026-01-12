import os
import tempfile
from pathlib import Path
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
from flask_cors import CORS
from pydub import AudioSegment
from openai import OpenAI

load_dotenv()

app = Flask(__name__)
# allow local dev frontend to call this API
CORS(app)

try:
    from pydub import AudioSegment
except Exception:
    AudioSegment = None


def convert_to_wav(src: Path) -> Path:
    if AudioSegment is None:
        raise RuntimeError("pydub not available; install requirements and ffmpeg")
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".wav")
    os.close(tmp_fd)
    audio = AudioSegment.from_file(str(src))
    audio.export(tmp_path, format="wav")
    return Path(tmp_path)


client = OpenAI()

def transcribe_with_openai(filepath: Path) -> str:
    with open(filepath, "rb") as f:
        resp = client.audio.transcriptions.create(
            file=f,
            model="whisper-1", #TODO make configurable
        )
    return resp.text

def analyze_with_crewai(text: str) -> dict:
    """Send `text` to the crewai_service /analyze endpoint and return its JSON response.

    Expects a running service at CREWAI_ANALYZE_URL (env) or http://localhost:6001/analyze.
    """
    url = os.getenv("CREWAI_ANALYZE_URL", "http://localhost:6001/analyze")
    try:
        resp = requests.post(url, json={"text": text}, timeout=15)
        try:
            return resp.json()
        except Exception:
            return {"error": "invalid JSON from analysis service", "status_code": resp.status_code, "text": resp.text}
    except Exception as e:
        return {"error": "request failed", "details": str(e)}


@app.route("/transcribe", methods=["POST"])
def transcribe():
    uploaded_tmp = None
    try:
        if "file" in request.files:
            f = request.files["file"]
            if f.filename == "":
                return jsonify({"error": "no file selected"}), 400
            suffix = Path(f.filename).suffix or ".wav"
            tmpf = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
            try:
                f.save(tmpf.name)
            finally:
                tmpf.close()
            src = Path(tmpf.name)
            uploaded_tmp = src
  
        tmp_wav = None
        try:
            # ensure we send a wav to transcription service
            if src.suffix.lower() != ".wav":
                tmp_wav = convert_to_wav(src)
                use_path = tmp_wav
            else:
                use_path = src

            # If OpenAI key is present and openai package installed, call it
            if os.getenv("OPENAI_API_KEY"):
                try:
                    text = transcribe_with_openai(use_path)
                except Exception as e:
                    return jsonify({"error": "transcription failed", "details": str(e)}), 500
            else:
                text = "OPENAI_API_KEY not set. Set the key to enable cloud transcription."

            # Attempt to send transcribed text to CrewAI analysis service
            analysis = analyze_with_crewai(text)

            return jsonify({"text": text, "analysis": analysis})
        finally:
            if tmp_wav and tmp_wav.exists():
                try:
                    tmp_wav.unlink()
                except Exception:
                    pass
    finally:
        # cleanup temporary uploaded file if present
        if uploaded_tmp and uploaded_tmp.exists():
            try:
                uploaded_tmp.unlink()
            except Exception:
                pass

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
