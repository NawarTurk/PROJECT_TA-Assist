# PROJECT_TAAI — Minimal run instructions

Prerequisites:
- Python 3.8+ and `pip`
- Node.js and `npm`
- `ffmpeg` installed on the system (pydub requires the binary): `brew install ffmpeg` (macOS)

Backend (API):

1. Install and run:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# set OPENAI_API_KEY in backend/.env
PORT=5001 python3 app.py
```

Frontend (React, Vite):

1. Install and run:
```bash
cd frontend
npm install
# dev (preferred — loads VITE_GATEWAY_URL from repo .env.local):
../scripts/start-frontend.sh
```
# open the dev URL printed by Vite (usually http://localhost:5173)
```

CrewAI analysis service:

1. Install and run:
```bash
cd crewai_service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# set CREWAI_API_KEY and/or OPENAI_API_KEY in crewai_service/.env
PORT=5002 python3 app.py
```

Notes:
- The backend expects the analysis service at `http://localhost:6001/analyze` by default. Set `CREWAI_ANALYZE_URL` to change it.
- Ensure `ffmpeg` is installed for audio conversion.
- `.env.example` files are present in the services — copy to `.env` and fill values.
