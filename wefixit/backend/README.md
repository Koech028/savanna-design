# WeFixIt Backend (FastAPI)

A minimal, secure API for Reviews and Portfolio with admin JWT auth.

## Quickstart (Local)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # then edit values as needed
uvicorn app.main:app --reload

