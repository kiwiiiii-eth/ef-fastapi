"""台電備轉資料的 Pydantic 模型"""
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class TaipowerReserveResponse(BaseModel):
    """台電備轉資料回應模型"""
    id: int
    tran_date: date
    tran_hour: int

    # 即時備轉 (SR - Spinning Reserve)
    sr_bid: Optional[float] = None
    sr_bid_qse: Optional[float] = None
    sr_bid_nontrade: Optional[float] = None
    sr_price: Optional[float] = None
    sr_perf_price_1: Optional[float] = None
    sr_perf_price_2: Optional[float] = None
    sr_perf_price_3: Optional[float] = None

    # 補充備轉 (SUP - Supplemental Reserve)
    sup_bid: Optional[float] = None
    sup_bid_qse: Optional[float] = None
    sup_bid_nontrade: Optional[float] = None
    sup_price: Optional[float] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaipowerStatisticsResponse(BaseModel):
    """台電統計資訊回應模型"""
    tran_date: date
    avg_sr_price: Optional[float] = None
    max_sr_price: Optional[float] = None
    min_sr_price: Optional[float] = None
    avg_sup_price: Optional[float] = None
    max_sup_price: Optional[float] = None
    min_sup_price: Optional[float] = None
    total_sr_capacity: Optional[float] = None
    total_sup_capacity: Optional[float] = None

    class Config:
        from_attributes = True