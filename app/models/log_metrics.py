from datetime import datetime
from sqlalchemy import ForeignKey, String, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.task import Task


class LogMetrics(Base):
    __tablename__ = "log_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="queued")
    execution_time_ms: Mapped[int] = mapped_column(Integer)
    message: Mapped[str] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    task:Mapped["Task"] = relationship(back_populates="log_metrics")
    
    # """Add later"""
    # cpu_usage_percent
    # memory_usage_mb
    # worker_id
    # retry_count
    # error_trace