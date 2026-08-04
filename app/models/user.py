from datetime import datetime
from uuid import UUID
from sqlalchemy import String, DateTime, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.identifier import generate_uuid

from .base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.task import Task

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    tasks: Mapped[list["Task"]] = relationship(back_populates="user")