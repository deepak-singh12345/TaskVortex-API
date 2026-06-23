from pydantic import BaseModel, Field, EmailStr
from typing import Literal

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Title of the task")
    description: str = Field(..., max_length=1000)
    task_type: Literal['data_extraction', 'report_generation', 'web_scraping']
    priority: int = Field(default=1, ge=1, le=5, description="Priority from 1 to 5")
    creator_email: EmailStr