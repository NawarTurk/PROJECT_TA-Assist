import os
import tempfile
from pathlib import Path
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
AUDIO_DIR = BASE_DIR / "audio"

try:
    from pydub import AudioSegment
except Exception:
    AudioSegment = None

try:
    import openai
except Exception:
    openai = None


def resolve_audio_path(rel_path: str) -> Path:
    if not rel_path:
        raise ValueError("empty path")
    # prevent path traversal
    candidate = (AUDIO_DIR / rel_path).resolve()
    if not str(candidate).startswith(str(AUDIO_DIR.resolve())):
        raise ValueError("invalid path")
    return candidate


def convert_to_wav(src: Path) -> Path:
    if AudioSegment is None:
        raise RuntimeError("pydub not available; install requirements and ffmpeg")
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".wav")
    os.close(tmp_fd)
    audio = AudioSegment.from_file(str(src))
    audio.export(tmp_path, format="wav")
    return Path(tmp_path)


from openai import OpenAI

client = OpenAI()

def transcribe_with_openai(filepath: Path) -> str:
    with open(filepath, "rb") as f:
        resp = client.audio.transcriptions.create(
            file=f,
            model="whisper-1",
        )
    return resp.text


@app.route("/transcribe", methods=["POST"])
def transcribe():
    data = request.get_json(force=True, silent=True)
    if not data or "path" not in data:
        return jsonify({"error": "missing 'path' in JSON body"}), 400
    rel_path = data["path"]
    try:
        src = resolve_audio_path(rel_path)
    except ValueError:
        return jsonify({"error": "invalid or disallowed path"}), 400
    if not src.exists():
        return jsonify({"error": "file not found", "path": str(src)}), 404

    tmp_wav = None
    try:
        # ensure we send a wav to transcription service
        if src.suffix.lower() != ".wav":
            tmp_wav = convert_to_wav(src)
            use_path = tmp_wav
        else:
            use_path = src

        # If OpenAI key is present and openai package installed, call it
        if os.getenv("OPENAI_API_KEY") and openai is not None:
            try:
                text = transcribe_with_openai(use_path)
            except Exception as e:
                return jsonify({"error": "transcription failed", "details": str(e)}), 500
        else:
            text = "OPENAI_API_KEY not set or openai package missing. Set the key to enable cloud transcription."

        return jsonify({"text": text})
    finally:
        if tmp_wav and tmp_wav.exists():
            try:
                tmp_wav.unlink()
            except Exception:
                pass

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
