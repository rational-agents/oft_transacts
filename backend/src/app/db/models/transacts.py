from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, BigInteger, CheckConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import Base

class Transact(Base):
    __tablename__ = "transacts"

    trans_id:   Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.account_id", ondelete="CASCADE"), nullable=False)

    occurred_at:  Mapped[datetime] = mapped_column(DateTime, nullable=False)
    amount_cents: Mapped[int] = mapped_column(BigInteger, nullable=False)  # positive integer cents
    direction:    Mapped[str] = mapped_column(String, nullable=False)   # 'credit' | 'debit'
    trans_status:       Mapped[str] = mapped_column(String, nullable=False, server_default=text("'posted'"))  # 'posted' | 'deleted'
    notes:        Mapped[str] = mapped_column(String, nullable=False)

    created_at:   Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        CheckConstraint("amount_cents >= 0", name="ck_amount_pos"),
        CheckConstraint("direction in ('credit','debit')", name="ck_direction"),
        CheckConstraint("trans_status in ('posted','deleted')", name="ck_tx_status"),
    )

    account: Mapped["Account"] = relationship(back_populates="transacts")