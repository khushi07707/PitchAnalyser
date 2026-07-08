import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class UploadResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    filename: str
    filepath: str
    file_size: int
    mime_type: str
    duration: Optional[float] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
