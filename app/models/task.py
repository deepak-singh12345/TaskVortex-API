from datetime import datetime
from typing import Any, Dict
from enum import Enum
from sqlalchemy import Enum as SQLEnum, Index
from uuid import UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import ForeignKey, String, Integer, DateTime, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship


from typing import TYPE_CHECKING

from app.core.identifier import generate_uuid

if TYPE_CHECKING:
    from app.models.user import User 
    from app.models.log_metrics import LogMetrics


from .base import Base

class TaskStatus(str, Enum):
    QUEUED = "queued"
    COMPLETED = "completed"
    FAILED = "failed"
    PROCESSING = "processing"

 
class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    task_type: Mapped[str] = mapped_column(String(50), nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=1)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    status: Mapped[TaskStatus] = mapped_column(SQLEnum(TaskStatus, values_callable=lambda enum_cls: [e.value for e in enum_cls]), default=TaskStatus.QUEUED)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    user:Mapped["User"] = relationship(back_populates="tasks")
    
    log_metrics: Mapped[list["LogMetrics"]] = relationship(back_populates="task", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("task_user_id_created_at_idx", "user_id", "created_at"),
    )