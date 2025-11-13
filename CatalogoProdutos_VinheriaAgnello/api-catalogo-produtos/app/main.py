from fastapi import FastAPI, HTTPException
from typing import List
import requests
import os
from .consul_register import register as consul_register
from model.Product import Product
from model.ProductCreate import ProductCreate

app = FastAPI()

# Simple in-memory DB
DB = {}
next_id = 1

CONSUL_HOST = os.getenv("CONSUL_HOST", "consul")
INVENTORY_SERVICE = os.getenv("INVENTORY_SERVICE", "inventory")

@app.on_event("startup")
def startup_event():
    try:
        consul_register()
    except Exception as e:
        print("consul register error (nonfatal):", e)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/v1/products", response_model=List[Product])
def get_all():
    return list(DB.values())

@app.get("/v1/products/{product_id}", response_model=Product)
def get_by_id(product_id: int):
    p = DB.get(product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Não encontrado")
    return p

@app.post("/v1/products", response_model=Product, status_code=201)
def create_product(payload: ProductCreate):
    global next_id
    product = Product(
        id=next_id,
        name=payload.name,
        price=payload.price
    )
    DB[next_id] = product
    next_id += 1
    return product

@app.put("/v1/products/{product_id}", response_model=Product)
def update_product(product_id: int, payload: ProductCreate):
    if product_id not in DB:
        raise HTTPException(status_code=404, detail="Não encontrado")
    updated = Product(id=product_id, name=payload.name, price=payload.price)
    DB[product_id] = updated
    return updated

@app.get("/v1/products/{product_id}/stock")
def check_stock(product_id: int):
    if product_id not in DB:
        raise HTTPException(status_code=404, detail="Não encontrado")
    try:
        resp = requests.get(f"http://{INVENTORY_SERVICE}/inventory/{product_id}", timeout=2)
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"inventory call failed: {e}")
