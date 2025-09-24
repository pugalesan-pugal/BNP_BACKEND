Backend (FastAPI)

Run locally (PowerShell):

```powershell
cd D:\backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env -ErrorAction SilentlyContinue
# Edit .env and set SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, ADMIN_TOKEN
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Endpoints:
- GET /health
- GET /products
- POST /products (admin)
- PATCH /products/{id} (admin)
- DELETE /products/{id} (admin)


