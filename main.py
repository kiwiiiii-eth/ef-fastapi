"""
FastAPI 虛擬電廠 (VPP) 系統主應用程式
提供太陽能、負載、台電備轉資料查詢 API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import vpp, taipower, upload
import os

# 建立 FastAPI 應用
app = FastAPI(
    title="虛擬電廠 (VPP) API",
    description="提供太陽能發電、負載數據、台電備轉容量查詢的 RESTful API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生產環境中應該設定具體的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(vpp.router, tags=["VPP 查詢"])
app.include_router(taipower.router, tags=["台電資料"])
app.include_router(upload.router, tags=["樹莓派上傳"])


@app.get("/")
def read_root():
    """
    首頁 - API 說明文件

    Returns:
        API 基本資訊和端點列表
    """
    return {
        "message": "歡迎使用虛擬電廠 (VPP) API",
        "version": "2.0.0",
        "framework": "FastAPI",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "vpp": {
                "realdata": "GET /api/vpp/realdata - 查詢所有場站即時數據",
                "realdata_site": "GET /api/vpp/realdata/{site_id} - 查詢特定場站即時數據",
                "solar_latest": "GET /api/vpp/solar/latest - 查詢最新太陽能數據",
                "solar_history": "GET /api/vpp/solar/history - 查詢太陽能歷史數據",
                "load_latest": "GET /api/vpp/load/latest - 查詢最新負載數據",
                "load_history": "GET /api/vpp/load/history - 查詢負載歷史數據",
                "summary": "GET /api/vpp/summary - 查詢彙總統計資訊"
            },
            "taipower": {
                "reserve_latest": "GET /api/taipower/reserve/latest - 查詢最新備轉資料",
                "reserve_date": "GET /api/taipower/reserve/date - 查詢特定日期備轉資料",
                "reserve_history": "GET /api/taipower/reserve/history - 查詢歷史備轉資料",
                "reserve_statistics": "GET /api/taipower/reserve/statistics - 查詢統計資訊",
                "reserve_hour": "GET /api/taipower/reserve/hour - 查詢特定時段資料"
            },
            "upload": {
                "upload": "POST /api/upload - 樹莓派數據上傳"
            }
        }
    }


@app.get("/health")
def health_check():
    """
    健康檢查端點

    Returns:
        系統狀態
    """
    return {
        "status": "healthy",
        "service": "VPP FastAPI"
    }


# 如果直接執行此檔案，啟動開發伺服器
if __name__ == "__main__":
    import uvicorn

    # 從環境變數取得端口，預設為 8000
    port = int(os.getenv("PORT", 8000))

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True  # 開發模式啟用自動重載
    )