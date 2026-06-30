# Running locally

## Backend
    cd backend
    python -m venv .venv && . .venv/bin/activate
    pip install -e ".[dev]"
    cp .env.example .env   # fill in keys
    uvicorn app.main:app --reload --port 8000

## Frontend
    cd frontend
    npm install
    cp .env.example .env    # VITE_API_BASE=http://localhost:8000
    npm run dev             # http://localhost:5173

## Tests
    cd backend && python -m pytest -v
    cd frontend && npm test
