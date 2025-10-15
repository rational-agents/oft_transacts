from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import Base

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email:   Mapped[str] = mapped_column(String, unique=True, nullable=False)  # Store as lowercase
    username:Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    accounts: Mapped[list["Account"]] = relationship(back_populates="user", cascade="all, delete-orphan")