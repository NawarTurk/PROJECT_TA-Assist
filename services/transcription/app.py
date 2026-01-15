import os
import tempfile
from pathlib import Path
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from pathlib import Path
from pydub import AudioSegment
from openai import OpenAI

# Prefer root .env.local when present (project root two levels up)
root = Path(__file__).resolve().parents[2]
env_local = root / '.env.local'
if env_local.exists():
    load_dotenv(dotenv_path=env_local)
else:
    load_dotenv()

app = Flask(__name__)

# Read OpenAI API key from environment and configure client
_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not _OPENAI_API_KEY:
    # do not hard-fail at import time; endpoints will return an error if key missing
    _OPENAI_API_KEY = None

client = OpenAI(api_key=_OPENAI_API_KEY) if _OPENAI_API_KEY else None


def convert_to_wav(src: Path) -> Path:
    tmp_fd, tmp_path = tempfile.mkstemp(suffix='.wav')
    os.close(tmp_fd)
    audio = AudioSegment.from_file(str(src))
    audio.export(tmp_path, format='wav')
    return Path(tmp_path)


def transcribe_with_openai(filepath: Path) -> str:
    if client is None:
        raise RuntimeError("OpenAI client not configured; set OPENAI_API_KEY")
    with open(filepath, 'rb') as f:
        resp = client.audio.transcriptions.create(file=f, model='whisper-1')
    # handle different client return shapes
    if isinstance(resp, dict):
        return resp.get('text') or str(resp)
    return getattr(resp, 'text', str(resp))


@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({'error': 'file required'}), 400
    f = request.files['file']
    if f.filename == '':
        return jsonify({'error': 'no file selected'}), 400

    suffix = Path(f.filename).suffix or '.wav'
    tmpf = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    try:
        f.save(tmpf.name)
    finally:
        tmpf.close()

    src = Path(tmpf.name)
    tmp_wav = None
    try:
        if src.suffix.lower() != '.wav':
            tmp_wav = convert_to_wav(src)
            use_path = tmp_wav
        else:
            use_path = src

        # ensure OPENAI_API_KEY is set
        if not os.getenv("OPENAI_API_KEY"):
            return jsonify({"error": "OPENAI_API_KEY not set"}), 500

        text = transcribe_with_openai(use_path)
        print(text)
        return jsonify({'text': text})
    finally:
        if tmp_wav and tmp_wav.exists():
            try:
                tmp_wav.unlink()
            except Exception:
                pass
        if src.exists():
            try:
                src.unlink()
            except Exception:
                pass


if __name__ == '__main__':
    PORT = int(os.getenv('TRANSCRIPTION_SERVICE_PORT', 5001))
    app.run(host='0.0.0.0', port=PORT, debug=True)
