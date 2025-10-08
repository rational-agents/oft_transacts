# backend/src/app/api/routers/accounts.py
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.deps import get_db, get_current_user_id
from app.db.models.accounts import Account

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.get("")
def list_my_accounts(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    rows = db.execute(select(Account).where(Account.user_id == user_id)).scalars().all()
    return [{"account_id": a.account_id, "account_name": a.account_name, "currency": a.currency} for a in rows]
