![CI](https://github.com/varunvss25/gks-demo/actions/workflows/ci.yml/badge.svg)

# GKS Demo — FDA Warning Letters Trends (Mini)
This demo ingests sample FDA **Warning Letters**, extracts **CFR citations**, and serves insights via **FastAPI** with a **React/TypeScript** dashboard. Includes QA checks, an audit trail, and a trend endpoint.

## Quickstart (Local, SQLite)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python pipeline.py
uvicorn app:app --reload --port 8000
```
Then in another terminal:
```bash
cd frontend
npm install
npm run dev
```
UI: http://localhost:5173 • API Docs: http://localhost:8000/docs

## Docker (Postgres + API + Web)
```bash
docker compose -f ops/docker-compose.yml up --build
```

## Endpoints
/top-cfr, /issuing-offices, /letters, /lineage, /top-cfr-trend, /health
