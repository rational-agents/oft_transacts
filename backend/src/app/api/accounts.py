# backend/src/app/api/routers/accounts.py
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.deps import get_db, get_current_user
from app.db.models.users import User
from app.db.models.accounts import Account
from app.db.models.account_balances import AccountBalance
from app.schemas import AccountWithBalance

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.get("", response_model=List[AccountWithBalance])
def list_my_accounts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Lists all accounts for the current user, including their latest balance."""
    stmt = (
        select(Account.account_id, Account.account_name, Account.currency, AccountBalance.balance)
        .join(AccountBalance, Account.account_id == AccountBalance.account_id)
        .where(Account.user_id == current_user.user_id)
    )
    rows = db.execute(stmt).all()
    # Manually construct the response to match the Pydantic model
    return [
        {
            "account_id": r.account_id,
            "account_name": r.account_name,
            "currency": r.currency,
            "balance": r.balance,
        }
        for r in rows
    ]
