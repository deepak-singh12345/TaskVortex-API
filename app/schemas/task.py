from pydantic import BaseModel, Field
from typing import Any, Literal

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Title of the task")
    description: str | None = Field(default=None, max_length=1000)
    # task_type: Literal['data_extraction', 'report_generation', 'web_scraping']
    complexity: Literal['light', 'heavy']
    priority: int = Field(default=1, ge=1, le=5, description="Priority from 1 to 5")
    payload: dict[str, Any]