"""
配置管理模組
統一管理應用程式的配置參數
"""
import os
from datetime import datetime, timezone, timedelta


class Config:
    """應用程式配置類別"""

    # 時區設定 (台灣時間 UTC+8)
    TIMEZONE = timezone(timedelta(hours=8))

    @staticmethod
    def get_current_time():
        """取得台灣當前時間"""
        return datetime.now(Config.TIMEZONE)

    # 資料庫配置（Zeabur PostgreSQL）
    # 優先使用 Zeabur 提供的環境變數，若無則使用舊的環境變數名稱
    POSTGRES_HOST = os.getenv('POSTGRES_HOST') or os.getenv('DATABASE_HOST', '43.153.175.27')
    POSTGRES_USER = os.getenv('POSTGRES_USER') or os.getenv('DATABASE_USER', 'root')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD') or os.getenv('DATABASE_PASSWORD', 'BZ2c6E3H7yDdpqwkn9l5SGt8ih10b4em')
    POSTGRES_DATABASE = os.getenv('POSTGRES_DATABASE') or os.getenv('DATABASE_NAME', 'zeabur')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT') or os.getenv('DATABASE_PORT', '31148')

    # 場站識別常數
    SITE_NORTH = 'north'
    SITE_CENTRAL = 'central'
    SITE_SOUTH = 'south'
    VALID_SITES = [SITE_NORTH, SITE_CENTRAL, SITE_SOUTH]

    # 資料類型常數
    DATA_TYPE_SOLAR = 'solar'
    DATA_TYPE_LOAD = 'load'
    DATA_TYPE_STORAGE = 'storage'

    # 外部 API 配置
    YIHONG_API_TOKEN = os.getenv('YIHONG_API_TOKEN', 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1bmlxdWVfbmFtZSI6InN1bndhcmUiLCJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9ndWlkIjoiYTMyZmM2ZjktZjYyYS00NDE3LThjMzEtMzViMDJmN2IyOGNkIiwicm9sZSI6InVzZXIiLCJpc3MiOiJsb2NhbGhvc3QiLCJhdWQiOiJhbGwiLCJleHAiOjE4MDM2MjY4NzgsIm5iZiI6MTc2OTY5MDg3OH0.hLPSHrdzB3uQOQE-k2OanY7XPUCE68xrPgEWAGUlYiI')
    YIHONG_API_URL = 'http://203.74.190.170/Solar-Yihong2-Api/api/Station/single-energy-report'