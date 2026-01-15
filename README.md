# PROJECT_TAAI

TA audio feedback system using microservices (transcription + analysis).

## Setup

1. **Clone & install:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r gateway/requirements.txt -r services/transcription/requirements.txt -r services/analysis/requirements.txt
```

2. **Configure `.env.local` at root:**
```dotenv
TRANSCRIPTION_SERVICE_PORT=5011
ANALYSIS_SERVICE_PORT=5012
GATEWAY_PORT=8888
OPENAI_API_KEY=sk-...
```

3. **Run services (3 terminals):**
```bash
# Terminal 1: Gateway
python gateway/app.py

# Terminal 2: Transcription
python services/transcription/app.py

# Terminal 3: Analysis
python services/analysis/app.py
```

4. **Run frontend (new terminal):**
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` (or port shown by Vite).

## Architecture

- **Gateway** (8888): Routes frontend requests to services
- **Transcription** (5011): Converts audio to text (OpenAI Whisper)
- **Analysis** (5012): Analyzes grammar & style (CrewAI)

## Requirements

- Python 3.8+, Node.js, ffmpeg (`brew install ffmpeg`)