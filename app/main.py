import os
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Hardcoded configuration per user request (no env variables)
SUPABASE_URL = "https://qbpydcfinpzvahfkcrzc.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFicHlkY2ZpbnB6dmFoZmtjcnpjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg3MjE4MjcsImV4cCI6MjA3NDI5NzgyN30.KmLnQsMlFK_rwItuvN8E_xt8-KXXkr3K0QMAeEEmcWY"
ADMIN_TOKEN = "jv52KKhbVtOayDVuKhGf+EYKWsjQzmP/aNM/AHfUYib3XqgPnNnuSZ2SZVJyRRi3"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

app = FastAPI(title="Amazon Clone Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProductIn(BaseModel):
    title: str
    price: float
    image_url: str | None = None
    rating: float | None = 0


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/products")
def list_products():
    res = supabase.table("products").select("id,title,price,image_url,rating,created_at").order("created_at", desc=True).limit(50).execute()
    return {"items": res.data or []}


@app.post("/products")
def create_product(payload: ProductIn, x_admin_token: str | None = Header(default=None)):
    if not ADMIN_TOKEN or x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")
    res = supabase.table("products").insert(payload.model_dump()).execute()
    if res.error:
        raise HTTPException(status_code=500, detail=str(res.error))
    return res.data[0] if res.data else {}


@app.patch("/products/{id}")
def update_product(id: str, payload: dict, x_admin_token: str | None = Header(default=None)):
    if not ADMIN_TOKEN or x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")
    res = supabase.table("products").update(payload).eq("id", id).execute()
    if res.error:
        raise HTTPException(status_code=500, detail=str(res.error))
    return res.data[0] if res.data else {}


@app.delete("/products/{id}")
def delete_product(id: str, x_admin_token: str | None = Header(default=None)):
    if not ADMIN_TOKEN or x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")
    res = supabase.table("products").delete().eq("id", id).execute()
    if res.error:
        raise HTTPException(status_code=500, detail=str(res.error))
    return {"ok": True}


