from fastapi import FastAPI, HTTPException
from typing import Dict, List
from .consul_register import register as consul_register
from app.model.BatchCreate import BatchCreate
from app.model.ReserveRequest import ReserveRequest
from app.model.Stock import Stock

app = FastAPI(title="Inventory API")

# in-memory
INVENTORY: Dict[int, List[Dict]] = {}

@app.on_event("startup")
def startup_event():
    try:
        consul_register()
    except Exception as e:
        print("consul register error (nonfatal):", e)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/v1/inventory/{product_id}")
def get_total_stock(product_id: int):
    """Retorna estoque disponível (não reservado) de um produto."""
    batches = INVENTORY.get(product_id, [])
    total_available = sum(b["qtd_disponivel"] for b in batches)
    return {"product_id": product_id, "total_disponivel": total_available}


@app.get("/v1/inventory/{product_id}/batches")
def get_batches(product_id: int):
    """Retorna info do lote."""
    return INVENTORY.get(product_id, [])


@app.post("/v1/inventory/{product_id}/batches")
def add_batch(product_id: int, batch: BatchCreate):
    """Adiciona um lote ao estoque."""
    if product_id not in INVENTORY:
        INVENTORY[product_id] = []

    INVENTORY[product_id].append({
        "batch_id": batch.batch_id,
        "qtd_disponivel": batch.quantity,
        "qtd_reservada": 0,
        "dt_validade": batch.expiration_date,
        "dt_entrada": batch.received_date
    })

    return {"message": "Lote adicionado ao estoque", "lotes": INVENTORY[product_id]}


@app.post("/v1/inventory/{product_id}/reserve")
def reserve(product_id: int, req: ReserveRequest):
    """Reserva sem tirar do estoque."""
    batches = INVENTORY.get(product_id)
    if not batches:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    needed = req.quantity

    for batch in sorted(batches, key=lambda b: b["dt_validade"]):  # FIFO 
        if needed <= 0:
            break

        available = batch["qtd_disponivel"]
        if available > 0:
            reserve_amount = min(available, needed)
            batch["qtd_disponivel"] -= reserve_amount
            batch["qtd_reservada"] += reserve_amount
            needed -= reserve_amount

    if needed > 0:
        raise HTTPException(status_code=409, detail="Não foi possível reservar: Estoque insuficiente")

    return {"message": "Reservado com sucesso", "lotes": batches}


@app.post("/v1/inventory/{product_id}/release")
def release(product_id: int, req: ReserveRequest):
    """Cancelamento de reserva."""
    batches = INVENTORY.get(product_id)
    if not batches:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    needed = req.quantity

    for batch in sorted(batches, key=lambda b: b["dt_validade"]):
        if needed <= 0:
            break

        reserved = batch["qtd_reservada"]
        if reserved > 0:
            release_amount = min(reserved, needed)
            batch["qtd_reservada"] -= release_amount
            batch["qtd_disponivel"] += release_amount
            needed -= release_amount

    if needed > 0:
        raise HTTPException(status_code=409, detail="Não foi possível cancelar a reserva: Não há reservas a serem canceladas")

    return {"message": "Reserva cancelada", "lotes": batches}


@app.post("/v1/inventory/{product_id}/consume")
def consume(product_id: int, req: ReserveRequest):
    """Finaliza reserva e retira do estoque (após venda)"""
    batches = INVENTORY.get(product_id)
    if not batches:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    needed = req.quantity

    for batch in sorted(batches, key=lambda b: b["dt_validade"]):
        if needed <= 0:
            break

        reserved = batch["qtd_reservada"]
        if reserved > 0:
            consume_amount = min(reserved, needed)
            batch["qtd_reservada"] -= consume_amount
            needed -= consume_amount

    if needed > 0:
        raise HTTPException(status_code=409, detail="Sem estoque reservado")

    return {"message": "Venda consumada", "lotes": batches}