from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from . import Base

class AccountBalance(Base):
    __tablename__ = "account_balances"
    account_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_name: Mapped[str] = mapped_column(String)
    currency: Mapped[str] = mapped_column(String)
    balance: Mapped[int] = mapped_column(Integer)