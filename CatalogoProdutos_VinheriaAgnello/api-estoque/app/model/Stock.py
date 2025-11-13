from pydantic import BaseModel

class Stock(BaseModel):
    product_id: int
    quantity: int