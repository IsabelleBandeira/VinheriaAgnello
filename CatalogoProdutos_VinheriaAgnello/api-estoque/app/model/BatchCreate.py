from pydantic import BaseModel

class BatchCreate(BaseModel):
    batch_id: str
    quantity: int
    expiration_date: str
    received_date: str