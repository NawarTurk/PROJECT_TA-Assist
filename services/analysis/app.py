import os
from dotenv import load_dotenv
from pathlib import Path
from flask import Flask, request, jsonify
from analysis import analyze_text

# Prefer root .env.local when present (project root two levels up)
root = Path(__file__).resolve().parents[2]
env_local = root / '.env.local'
if env_local.exists():
    load_dotenv(dotenv_path=env_local)
else:
    load_dotenv()

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json(silent=True) or {}
    text = data.get('text', '')
    if not text.strip():
        return jsonify({'error': 'text is required'}), 400
    # ensure OPENAI_API_KEY is available for downstream LLM calls
    if not os.getenv('OPENAI_API_KEY'):
        return jsonify({'error': 'OPENAI_API_KEY not set'}), 500

    try:
        result = analyze_text(text)
        return jsonify({'analysis': result})
    except Exception as e:
        return jsonify({'error': 'analysis failed', 'details': str(e)}), 500


if __name__ == '__main__':
    PORT = int(os.getenv('ANALYSIS_SERVICE_PORT'))
    app.run(host='0.0.0.0', port=PORT, debug=True)
