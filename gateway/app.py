import os
from dotenv import load_dotenv
from pathlib import Path
from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

# Prefer root .env.local when present (project root one level up)
root = Path(__file__).resolve().parents[1]
env_local = root / '.env.local'
if env_local.exists():
    load_dotenv(dotenv_path=env_local)
else:
    load_dotenv()

app = Flask(__name__)
CORS(app)

TRANSCRIPTION_URL = os.getenv('TRANSCRIPTION_SERVICE_URL', 'http://localhost:5001/transcribe')
ANALYSIS_URL = os.getenv('ANALYSIS_SERVICE_URL', 'http://localhost:5002/analyze')


@app.route('/transcribe', methods=['POST'])
def transcribe_gateway():
    # expect multipart file upload from frontend
    if 'file' not in request.files:
        return jsonify({'error': 'file required'}), 400
    f = request.files['file']
    if f.filename == '':
        return jsonify({'error': 'no file selected'}), 400

    files = {'file': (f.filename, f.stream, f.mimetype)}
    try:
        # forward to transcription service
        print('Sending file to transcription service...')
        r = requests.post(TRANSCRIPTION_URL, files=files, timeout=60)
    except Exception as e:
        return jsonify({'error': 'transcription service request failed', 'details': str(e)}), 502

    try:
        trans_resp = r.json()
    except Exception:
        return jsonify({'error': 'invalid JSON from transcription service', 'status_code': r.status_code, 'text': r.text}), 502

    text = trans_resp.get('text')

    # call analysis service
    try:
        print('Sending text to analysis service...')
        a = requests.post(ANALYSIS_URL, json={'text': text}, timeout=20)
        analysis = a.json() if a.status_code == 200 else {'error': 'analysis service error', 'status_code': a.status_code, 'text': a.text}
    except Exception as e:
        analysis = {'error': 'analysis request failed', 'details': str(e)}
    print(jsonify({'text': text, 'analysis': analysis, 'transcription_raw': trans_resp}))
    return jsonify({'text': text, 'analysis': analysis, 'transcription_raw': trans_resp})


if __name__ == '__main__':
    # prefer explicit gateway port, fall back to generic SERVICE_PORT
    PORT = int(os.getenv('GATEWAY_PORT', os.getenv('SERVICE_PORT')))
    app.run(host='0.0.0.0', port=PORT, debug=True)
