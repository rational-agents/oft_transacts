# backend/src/app/schemas.py
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import List, Optional

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
    amount_cents: int = Field(..., gt=0, le=9223372036854775807, description="Amount in cents (supports large values)")
    direction: str  # 'credit' | 'debit'
    
    @validator('amount_cents')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        if v > 9223372036854775807:  # PostgreSQL BIGINT max
            raise ValueError('Amount exceeds maximum allowed value')
        return v

class UpdateTransactRequest(BaseModel):
    notes: Optional[str] = None
    amount_cents: Optional[int] = Field(None, gt=0, le=9223372036854775807, description="Amount in cents (supports large values)")
    direction: Optional[str] = None  # 'credit' | 'debit'
    trans_status: Optional[str] = None  # 'posted' | 'deleted'
    
    @validator('amount_cents')
    def validate_amount(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError('Amount must be greater than 0')
            if v > 9223372036854775807:  # PostgreSQL BIGINT max
                raise ValueError('Amount exceeds maximum allowed value')
        return v