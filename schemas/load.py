"""負載數據的 Pydantic 模型"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LoadDataResponse(BaseModel):
    """負載數據回應模型"""
    id: int
    site_id: str
    datetime: datetime
    load_value: Optional[float] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True