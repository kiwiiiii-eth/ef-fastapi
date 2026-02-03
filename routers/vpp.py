"""
VPP 查詢端點
提供虛擬電廠系統查詢即時和歷史數據的 API（FastAPI 版本）
"""
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from config import Config
from models import SolarDataModel, LoadDataModel
from utils.db import execute_query, row_to_dict

router = APIRouter()


@router.get('/api/vpp/realdata')
def get_realdata() -> Dict[str, Any]:
    """
    查詢所有場站的最新即時數據（太陽能 + 負載）

    Returns:
        JSON: {
            "timestamp": "2026-01-29T20:00:00",
            "sites": {
                "north": {
                    "solar": { ... },
                    "load": { ... }
                },
                "central": { ... },
                "south": { ... }
            }
        }
    """
    try:
        # 查詢所有場站的最新太陽能數據
        solar_rows = execute_query(SolarDataModel.SELECT_ALL_LATEST_SQL, fetch=True)

        # 查詢所有場站的最新負載數據
        load_rows = execute_query(LoadDataModel.SELECT_ALL_LATEST_SQL, fetch=True)

        # 組織數據結構
        sites_data = {}
        current_time = Config.get_current_time().isoformat()

        # 處理太陽能數據
        for row in solar_rows:
            site_id = row['site_id']
            if site_id not in sites_data:
                sites_data[site_id] = {"solar": None, "load": None}

            sites_data[site_id]['solar'] = {
                "datetime": row['datetime'].isoformat() if row['datetime'] else None,
                "daily_generation": float(row['daily_generation']) if row['daily_generation'] else 0,
                "solar_radiation": float(row['solar_radiation']) if row['solar_radiation'] else 0,
                "ac_avg_voltage": float(row['ac_avg_voltage']) if row['ac_avg_voltage'] else 0,
                "ac_total_power": float(row['ac_total_power']) if row['ac_total_power'] else 0,
                "ac_total_current": float(row['ac_total_current']) if row['ac_total_current'] else 0,
                "dc_avg_voltage": float(row['dc_avg_voltage']) if row['dc_avg_voltage'] else 0,
                "dc_total_power": float(row['dc_total_power']) if row['dc_total_power'] else 0,
                "dc_total_current": float(row['dc_total_current']) if row['dc_total_current'] else 0,
                "module_temperature": float(row['module_temperature']) if row['module_temperature'] else 0,
                "total_accumulated_generation": float(row['total_accumulated_generation']) if row['total_accumulated_generation'] else 0,
                "co2_reduction": float(row['co2_reduction']) if row['co2_reduction'] else 0
            }

        # 處理負載數據
        for row in load_rows:
            site_id = row['site_id']
            if site_id not in sites_data:
                sites_data[site_id] = {"solar": None, "load": None}

            sites_data[site_id]['load'] = {
                "datetime": row['datetime'].isoformat() if row['datetime'] else None,
                "value": float(row['load_value']) if row['load_value'] else 0
            }

        return {
            "timestamp": current_time,
            "sites": sites_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢失敗: {str(e)}")


@router.get('/api/vpp/realdata/{site_id}')
def get_site_realdata(site_id: str) -> Dict[str, Any]:
    """
    查詢特定場站的最新即時數據

    Args:
        site_id: 場站識別碼 (north/central/south)

    Returns:
        JSON: {
            "site_id": "north",
            "timestamp": "2026-01-29T20:00:00",
            "solar": { ... },
            "load": { ... }
        }
    """
    try:
        # 驗證場站 ID
        if site_id not in Config.VALID_SITES:
            raise HTTPException(
                status_code=400,
                detail=f"無效的場站 ID，必須是 {', '.join(Config.VALID_SITES)} 之一"
            )

        # 查詢太陽能數據
        solar_row = execute_query(
            SolarDataModel.SELECT_LATEST_SQL,
            (site_id,),
            fetch_one=True
        )

        # 查詢負載數據
        load_row = execute_query(
            LoadDataModel.SELECT_LATEST_SQL,
            (site_id,),
            fetch_one=True
        )

        # 組織回傳數據
        result = {
            "site_id": site_id,
            "timestamp": Config.get_current_time().isoformat(),
            "solar": row_to_dict(solar_row) if solar_row else None,
            "load": row_to_dict(load_row) if load_row else None
        }

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢失敗: {str(e)}")


@router.get('/api/vpp/solar/latest')
def get_solar_latest(site_id: Optional[str] = Query(None, description="場站識別碼（可選）")) -> Any:
    """
    查詢最新太陽能數據

    Query Parameters:
        site_id (optional): 篩選特定場站

    Returns:
        JSON: 太陽能數據列表或單筆數據
    """
    try:
        if site_id:
            # 查詢特定場站
            if site_id not in Config.VALID_SITES:
                raise HTTPException(
                    status_code=400,
                    detail=f"無效的場站 ID，必須是 {', '.join(Config.VALID_SITES)} 之一"
                )

            row = execute_query(
                SolarDataModel.SELECT_LATEST_SQL,
                (site_id,),
                fetch_one=True
            )
            return row_to_dict(row)
        else:
            # 查詢所有場站
            rows = execute_query(SolarDataModel.SELECT_ALL_LATEST_SQL, fetch=True)
            return [row_to_dict(row) for row in rows]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢失敗: {str(e)}")


@router.get('/api/vpp/solar/history')
def get_solar_history(
    site_id: str = Query(..., description="場站識別碼（必填）"),
    start_date: Optional[str] = Query(None, description="起始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="結束日期 (YYYY-MM-DD)"),
    limit: int = Query(1000, description="限制筆數", ge=1, le=10000)
) -> Dict[str, Any]:
    """
    查詢太陽能歷史數據

    Query Parameters:
        site_id (required): 場站識別碼
        start_date (optional): 起始日期 (YYYY-MM-DD)，預設為 7 天前
        end_date (optional): 結束日期 (YYYY-MM-DD)，預設為今天
        limit (optional): 限制筆數，預設 1000

    Returns:
        JSON: 歷史數據列表
    """
    try:
        # 驗證場站 ID
        if site_id not in Config.VALID_SITES:
            raise HTTPException(
                status_code=400,
                detail=f"必須提供有效的場站 ID ({', '.join(Config.VALID_SITES)})"
            )

        # 取得日期範圍 (使用台灣時間)
        if end_date:
            # 將結束日期設為當天的 23:59:59
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
        else:
            end_dt = Config.get_current_time().replace(tzinfo=None)

        if start_date:
            # 將開始日期設為當天的 00:00:00
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            start_dt = start_dt.replace(hour=0, minute=0, second=0)
        else:
            start_dt = end_dt - timedelta(days=7)

        # 查詢歷史數據
        rows = execute_query(
            SolarDataModel.SELECT_HISTORY_SQL,
            (site_id, start_dt, end_dt, limit),
            fetch=True
        )

        return {
            "site_id": site_id,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "count": len(rows),
            "data": [row_to_dict(row) for row in rows]
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"日期格式錯誤: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢失敗: {str(e)}")


@router.get('/api/vpp/load/latest')
def get_load_latest(site_id: Optional[str] = Query(None, description="場站識別碼（可選）")) -> Any:
    """
    查詢最新負載數據

    Query Parameters:
        site_id (optional): 篩選特定場站

    Returns:
        JSON: 負載數據列表或單筆數據
    """
    try:
        if site_id:
            # 查詢特定場站
            if site_id not in Config.VALID_SITES:
                raise HTTPException(
                    status_code=400,
                    detail=f"無效的場站 ID，必須是 {', '.join(Config.VALID_SITES)} 之一"
                )

            row = execute_query(
                LoadDataModel.SELECT_LATEST_SQL,
                (site_id,),
                fetch_one=True
            )
            return row_to_dict(row)
        else:
            # 查詢所有場站
            rows = execute_query(LoadDataModel.SELECT_ALL_LATEST_SQL, fetch=True)
            return [row_to_dict(row) for row in rows]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢失敗: {str(e)}")


@router.get('/api/vpp/load/history')
def get_load_history(
    site_id: str = Query(..., description="場站識別碼（必填）"),
    start_date: Optional[str] = Query(None, description="起始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="結束日期 (YYYY-MM-DD)"),
    limit: int = Query(1000, description="限制筆數", ge=1, le=10000)
) -> Dict[str, Any]:
    """
    查詢負載歷史數據

    Query Parameters:
        site_id (required): 場站識別碼
        start_date (optional): 起始日期，預設為 7 天前
        end_date (optional): 結束日期，預設為今天
        limit (optional): 限制筆數，預設 1000

    Returns:
        JSON: 歷史數據列表
    """
    try:
        # 驗證場站 ID
        if site_id not in Config.VALID_SITES:
            raise HTTPException(
                status_code=400,
                detail=f"必須提供有效的場站 ID ({', '.join(Config.VALID_SITES)})"
            )

        # 取得日期範圍 (使用台灣時間)
        if end_date:
            # 將結束日期設為當天的 23:59:59
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
        else:
            end_dt = Config.get_current_time().replace(tzinfo=None)

        if start_date:
            # 將開始日期設為當天的 00:00:00
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            start_dt = start_dt.replace(hour=0, minute=0, second=0)
        else:
            start_dt = end_dt - timedelta(days=7)

        # 查詢歷史數據
        rows = execute_query(
            LoadDataModel.SELECT_HISTORY_SQL,
            (site_id, start_dt, end_dt, limit),
            fetch=True
        )

        return {
            "site_id": site_id,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "count": len(rows),
            "data": [row_to_dict(row) for row in rows]
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"日期格式錯誤: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢失敗: {str(e)}")


@router.get('/api/vpp/summary')
def get_summary() -> Dict[str, Any]:
    """
    查詢彙總統計資訊

    Returns:
        JSON: {
            "timestamp": "2026-01-29T20:00:00",
            "total_sites": 3,
            "summary": {
                "total_generation": 2500.0,
                "total_load": 1800.0,
                "net_generation": 700.0
            },
            "sites": [ ... ]
        }
    """
    try:
        # 查詢所有場站的最新太陽能數據
        solar_rows = execute_query(SolarDataModel.SELECT_ALL_LATEST_SQL, fetch=True)

        # 查詢所有場站的最新負載數據
        load_rows = execute_query(LoadDataModel.SELECT_ALL_LATEST_SQL, fetch=True)

        # 計算統計資訊
        total_generation = sum(
            float(row['daily_generation']) if row['daily_generation'] else 0
            for row in solar_rows
        )

        total_load = sum(
            float(row['load_value']) if row['load_value'] else 0
            for row in load_rows
        )

        # 組織各場站資訊
        sites_summary = []
        for row in solar_rows:
            sites_summary.append({
                "site_id": row['site_id'],
                "daily_generation": float(row['daily_generation']) if row['daily_generation'] else 0,
                "ac_total_power": float(row['ac_total_power']) if row['ac_total_power'] else 0
            })

        return {
            "timestamp": Config.get_current_time().isoformat(),
            "total_sites": len(Config.VALID_SITES),
            "summary": {
                "total_generation": total_generation,
                "total_load": total_load,
                "net_generation": total_generation - total_load
            },
            "sites": sites_summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢失敗: {str(e)}")