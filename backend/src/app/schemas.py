# backend/src/app/schemas.py
from pydantic import BaseModel

class UserProfile(BaseModel):
    username: str
    email: str

    class Config:
        from_attributes = True

class AccountWithBalance(BaseModel):
    account_id: int
    account_name: str
    currency: str
    balance: int

    class Config:
        from_attributes = True
