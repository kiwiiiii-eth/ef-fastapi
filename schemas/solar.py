"""太陽能數據的 Pydantic 模型"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SolarDataResponse(BaseModel):
    """太陽能數據回應模型"""
    id: int
    site_id: str
    datetime: datetime
    daily_generation: Optional[float] = None
    solar_radiation: Optional[float] = None
    ac_avg_voltage: Optional[float] = None
    ac_total_power: Optional[float] = None
    ac_total_current: Optional[float] = None
    dc_avg_voltage: Optional[float] = None
    dc_total_power: Optional[float] = None
    dc_total_current: Optional[float] = None
    module_temperature: Optional[float] = None
    total_accumulated_generation: Optional[float] = None
    co2_reduction: Optional[float] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
