# backend/src/app/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import List

class UserProfile(BaseModel):
    username: str
    email: str

    class Config:
        orm_mode = True  # Changed from from_attributes

class AccountWithBalance(BaseModel):
    account_id: int
    account_name: str
    currency: str
    balance: int

    class Config:
        orm_mode = True  # Changed from from_attributes


class TransactResponse(BaseModel):
    trans_id: int
    account_id: int
    occurred_at: datetime
    amount_cents: int
    direction: str  # 'credit' | 'debit'
    trans_status: str  # 'posted' | 'deleted'
    notes: str
    
    class Config:
        orm_mode = True  # Changed from from_attributes

class TransactsPage(BaseModel):
    items: List[TransactResponse]
    total: int
    page: int
    page_size: int
    has_more: bool

class CreateTransactRequest(BaseModel):
    notes: str
    amount_cents: int
    direction: str  # 'credit' | 'debit'