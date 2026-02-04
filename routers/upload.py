"""
樹莓派數據上傳端點
保留原有的 /api/upload 功能（FastAPI 版本）
"""
import psycopg2
from fastapi import APIRouter, HTTPException, status
from schemas.upload import UploadRequest, UploadResponse
from utils.db import get_db_connection

router = APIRouter()


@router.post('/api/upload', status_code=status.HTTP_201_CREATED, response_model=UploadResponse)
def upload_data(data: UploadRequest) -> UploadResponse:
    """
    接收樹莓派傳來的數據並存儲到 stu 表

    Request JSON:
        {
            "device_id": "pi_001",
            "value": 24.5,
            "timestamp": "2026-01-22 14:30:05"
        }

    Returns:
        JSON: {"message": "success", "data": {...}} 或錯誤訊息
    """
    try:
        # 正確使用連線池 context manager
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # 插入數據到 stu 表
            query = "INSERT INTO stu (device_id, value, timestamp) VALUES (%s, %s, %s)"
            cursor.execute(query, (data.device_id, data.value, data.timestamp))

            conn.commit()
            cursor.close()

            return UploadResponse(
                message="success",
                data={
                    "device_id": data.device_id,
                    "value": data.value,
                    "timestamp": data.timestamp
                }
            )

    except psycopg2.Error as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {err}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
        )