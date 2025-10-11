# backend/src/app/api/transacts.py
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.deps import get_db, get_current_user
from app.db.models.users import User
from app.db.models.accounts import Account
from app.db.models.transacts import Transact
from app.schemas import TransactsPage, TransactResponse, CreateTransactRequest
from app.core.config import get_settings
from datetime import datetime

router = APIRouter(prefix="/accounts", tags=["transacts"])

@router.get("/{account_id}/transacts", response_model=TransactsPage)
def get_account_transacts(
    account_id: int,
    page: int = Query(1, ge=1),
    page_size: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch paginated transactions for a specific account.
    
    - Fetches ALL transactions (both posted and deleted)
    - Orders by occurred_at DESC (most recent first)
    - Returns paginated results with metadata
    """
    settings = get_settings()
    
    # Use provided page_size or default from config
    if page_size is None:
        page_size = settings.transacts_page_size
    
    # Authorization: verify the account belongs to the current user
    account = db.scalar(
        select(Account).where(
            Account.account_id == account_id,
            Account.user_id == current_user.user_id
        )
    )
    
    if not account:
        raise HTTPException(status_code=403, detail="Access denied to this account")
    
    # Build query for ALL transactions (no trans_status filter)
    base_query = select(Transact).where(
        Transact.account_id == account_id
    ).order_by(Transact.occurred_at.desc())
    
    # Get total count
    total = db.scalar(
        select(func.count()).select_from(
            base_query.subquery()
        )
    )
    
    # Get paginated items
    offset = (page - 1) * page_size
    items = db.scalars(
        base_query.limit(page_size).offset(offset)
    ).all()
    
    # Check if there are more items
    has_more = (offset + page_size) < total
    
    return TransactsPage(
        items=[TransactResponse.from_orm(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        has_more=has_more
    )

@router.post("/{account_id}/transacts", response_model=TransactResponse, status_code=201)
def create_account_transact(
    account_id: int,
    transact_data: CreateTransactRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new transaction for a specific account.
    
    - Verifies account ownership
    - Sets status to 'posted' by default
    - Sets occurred_at to current timestamp
    - Returns the created transaction
    """
    # Authorization: verify the account belongs to the current user
    account = db.scalar(
        select(Account).where(
            Account.account_id == account_id,
            Account.user_id == current_user.user_id
        )
    )
    
    if not account:
        raise HTTPException(status_code=403, detail="Access denied to this account")
    
    # Validate direction
    if transact_data.direction not in ('credit', 'debit'):
        raise HTTPException(status_code=400, detail="Direction must be 'credit' or 'debit'")
    
    # Validate amount
    if transact_data.amount_cents <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")
    
    # Create new transaction
    new_transact = Transact(
        account_id=account_id,
        occurred_at=datetime.utcnow(),
        amount_cents=transact_data.amount_cents,
        direction=transact_data.direction,
        trans_status='posted',
        notes=transact_data.notes
    )
    
    db.add(new_transact)
    db.commit()
    db.refresh(new_transact)
    
    return TransactResponse.from_orm(new_transact)