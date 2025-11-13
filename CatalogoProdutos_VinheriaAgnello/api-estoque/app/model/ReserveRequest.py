from pydantic import BaseModel

class ReserveRequest(BaseModel):
    quantity: int