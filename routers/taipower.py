"""
台電備轉資料查詢端點
提供台電電力交易平台備轉容量與價格資料的 API（FastAPI 版本）
"""
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta, date
from typing import Optional, Dict, Any, List
from config import Config
from models import TaipowerReserveModel
from utils.db import execute_query

router = APIRouter()


def row_to_dict(row):
    """將資料庫 Row 物件轉換為字典"""
    if row is None:
        return None
    return dict(row)


@router.get('/api/taipower/reserve/latest')
def get_latest_reserve() -> Dict[str, Any]:
    """
    查詢最新一天的備轉資料 (24 筆)

    Returns:
        JSON: {
            "date": "2026-02-03",
            "count": 24,
            "data": [
                {
                    "tran_hour": 0,
                    "sr_price": 50.0,
                    "sup_price": 30.0,
                    ...
                },
                ...
            ]
        }
    """
    try:
        rows = execute_query(TaipowerReserveModel.SELECT_LATEST_DAY_SQL, fetch=True)

        if not rows:
            raise HTTPException(
                status_code=404,
                detail="尚無資料，資料庫中沒有任何備轉資料"
            )

        data = [row_to_dict(row) for row in rows]

        return {
            "date": data[0]['tran_date'].strftime('%Y-%m-%d') if data else None,
            "count": len(data),
            "data": data
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢失敗: {str(e)}")


@router.get('/api/taipower/reserve/date')
def get_reserve_by_date(
    date: str = Query(..., description="日期 (YYYY-MM-DD)")
) -> Dict[str, Any]:
    """
    查詢特定日期的備轉資料

    Query Parameters:
        date (required): 日期 (YYYY-MM-DD)

    Returns:
        JSON: {
            "date": "2026-02-03",
            "count": 24,
            "data": [ ... ]
        }
    """
    try:
        # 驗證日期格式
        try:
            target_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="日期格式錯誤，日期格式必須為 YYYY-MM-DD"
            )

        # 查詢資料
        rows = execute_query(
            TaipowerReserveModel.SELECT_BY_DATE_SQL,
            (target_date,),
            fetch=True
        )

        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"查無資料，{date} 沒有備轉資料"
            )

        data = [row_to_dict(row) for row in rows]

        return {
            "date": date,
            "count": len(data),
            "data": data
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢失敗: {str(e)}")


@router.get('/api/taipower/reserve/history')
def get_reserve_history(
    start_date: Optional[str] = Query(None, description="起始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="結束日期 (YYYY-MM-DD)"),
    limit: int = Query(1000, description="限制筆數", ge=1, le=10000)
) -> Dict[str, Any]:
    """
    查詢歷史備轉資料

    Query Parameters:
        start_date (optional): 起始日期 (YYYY-MM-DD)，預設為 7 天前
        end_date (optional): 結束日期 (YYYY-MM-DD)，預設為今天
        limit (optional): 限制筆數，預設 1000

    Returns:
        JSON: {
            "start_date": "2026-01-27",
            "end_date": "2026-02-03",
            "count": 168,
            "data": [ ... ]
        }
    """
    try:
        # 取得日期範圍 (使用台灣時間)
        if end_date:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_dt = Config.get_current_time().date()

        if start_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            start_dt = end_dt - timedelta(days=7)

        # 查詢歷史數據
        rows = execute_query(
            TaipowerReserveModel.SELECT_HISTORY_SQL,
            (start_dt, end_dt, limit),
            fetch=True
        )

        data = [row_to_dict(row) for row in rows]

        return {
            "start_date": start_dt.strftime('%Y-%m-%d'),
            "end_date": end_dt.strftime('%Y-%m-%d'),
            "count": len(data),
            "data": data
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"日期格式錯誤: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢失敗: {str(e)}")


@router.get('/api/taipower/reserve/statistics')
def get_reserve_statistics(
    date: Optional[str] = Query(None, description="日期 (YYYY-MM-DD)，預設為今天")
) -> Dict[str, Any]:
    """
    查詢特定日期的統計資訊

    Query Parameters:
        date (optional): 日期 (YYYY-MM-DD)，預設為今天

    Returns:
        JSON: {
            "date": "2026-02-03",
            "statistics": {
                "sr": {
                    "avg_price": 52.5,
                    "max_price": 80.0,
                    "min_price": 30.0,
                    "total_capacity": 12000.0
                },
                "sup": {
                    "avg_price": 35.2,
                    "max_price": 50.0,
                    "min_price": 25.0,
                    "total_capacity": 24000.0
                }
            }
        }
    """
    try:
        # 取得日期參數
        if date:
            target_date = datetime.strptime(date, '%Y-%m-%d').date()
        else:
            target_date = Config.get_current_time().date()

        # 查詢統計資料
        row = execute_query(
            TaipowerReserveModel.SELECT_STATISTICS_SQL,
            (target_date,),
            fetch_one=True
        )

        if not row:
            raise HTTPException(
                status_code=404,
                detail=f"查無資料，{target_date.strftime('%Y-%m-%d')} 沒有備轉資料"
            )

        # 組織回傳資料
        result = {
            "date": target_date.strftime('%Y-%m-%d'),
            "statistics": {
                "sr": {
                    "avg_price": float(row['avg_sr_price']) if row['avg_sr_price'] else 0,
                    "max_price": float(row['max_sr_price']) if row['max_sr_price'] else 0,
                    "min_price": float(row['min_sr_price']) if row['min_sr_price'] else 0,
                    "total_capacity": float(row['total_sr_capacity']) if row['total_sr_capacity'] else 0
                },
                "sup": {
                    "avg_price": float(row['avg_sup_price']) if row['avg_sup_price'] else 0,
                    "max_price": float(row['max_sup_price']) if row['max_sup_price'] else 0,
                    "min_price": float(row['min_sup_price']) if row['min_sup_price'] else 0,
                    "total_capacity": float(row['total_sup_capacity']) if row['total_sup_capacity'] else 0
                }
            }
        }

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"日期格式錯誤: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢失敗: {str(e)}")


@router.get('/api/taipower/reserve/hour')
def get_reserve_by_hour(
    date: str = Query(..., description="日期 (YYYY-MM-DD)"),
    hour: int = Query(..., description="時段 (0-23)", ge=0, le=23)
) -> Dict[str, Any]:
    """
    查詢特定日期和時段的備轉資料

    Query Parameters:
        date (required): 日期 (YYYY-MM-DD)
        hour (required): 時段 (0-23)

    Returns:
        JSON: 單筆資料
    """
    try:
        # 驗證參數
        target_date = datetime.strptime(date, '%Y-%m-%d').date()

        # 查詢資料
        sql = """
        SELECT * FROM taipower_reserve_data
        WHERE tran_date = %s AND tran_hour = %s
        """
        row = execute_query(sql, (target_date, hour), fetch_one=True)

        if not row:
            raise HTTPException(
                status_code=404,
                detail=f"查無資料，{date} {hour}:00 沒有備轉資料"
            )

        return row_to_dict(row)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"參數格式錯誤: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢失敗: {str(e)}")