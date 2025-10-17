from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, DateTime, ForeignKey, BigInteger, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import Base

class Account(Base):
    __tablename__ = "accounts"

    account_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id:    Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    account_name:       Mapped[str] = mapped_column(String, nullable=False)
    currency:   Mapped[str] = mapped_column(String, nullable=False, server_default=text("'USD'"))

    # checkpoint value + timestamp (TEXT in SQL, mapped as datetime here)
    checkpoint_balance: Mapped[int] = mapped_column(BigInteger, nullable=False)
    checkpoint_timestamp:            Mapped[datetime] = mapped_column(DateTime, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="accounts")
    transacts: Mapped[list["Transact"]] = relationship(back_populates="account", cascade="all, delete-orphan")   