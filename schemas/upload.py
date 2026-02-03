"""樹莓派上傳數據的 Pydantic 模型"""
from pydantic import BaseModel, Field
from typing import Optional


class UploadRequest(BaseModel):
    """樹莓派上傳請求模型"""
    device_id: str = Field(..., description="設備識別碼")
    value: float = Field(..., description="數據值")
    timestamp: str = Field(..., description="時間戳記（格式：YYYY-MM-DD HH:MM:SS）")

    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "pi_001",
                "value": 24.5,
                "timestamp": "2026-02-03 14:30:05"
            }
        }


class UploadResponse(BaseModel):
    """上傳回應模型"""
    message: str
    data: Optional[dict] = None