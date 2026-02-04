"""
FastAPI 虛擬電廠 (VPP) 系統主應用程式
提供太陽能、負載、台電備轉資料查詢 API
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routers import vpp, taipower, upload
import os
import time
from collections import defaultdict
import threading

# 建立 FastAPI 應用
app = FastAPI(
    title="虛擬電廠 (VPP) API",
    description="提供太陽能發電、負載數據、台電備轉容量查詢的 RESTful API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 速率限制器
class RateLimiter:
    def __init__(self, requests_per_minute=30):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
        self.lock = threading.Lock()

    def is_allowed(self, client_ip: str, path: str) -> bool:
        """檢查是否允許請求"""
        now = time.time()
        key = f"{client_ip}:{path}"

        with self.lock:
            # 清除 60 秒前的請求記錄
            self.requests[key] = [req_time for req_time in self.requests[key] if now - req_time < 60]

            # 檢查是否超過限制
            if len(self.requests[key]) >= self.requests_per_minute:
                return False

            # 記錄本次請求
            self.requests[key].append(now)
            return True

rate_limiter = RateLimiter(requests_per_minute=30)  # 每分鐘最多 30 個請求

# 速率限制中介軟體（目前停用，因為前端透過內網都是同一個 IP）
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # 暫時停用速率限制
    # 原因：前端透過 Zeabur 內網請求，所有請求都來自 10.42.0.1
    # 會誤判為同一個使用者而被限制

    # if request.url.path.startswith("/api/"):
    #     client_ip = request.client.host
    #     if not rate_limiter.is_allowed(client_ip, request.url.path):
    #         raise HTTPException(
    #             status_code=429,
    #             detail="請求過於頻繁，請稍後再試（每分鐘最多 30 個請求）"
    #         )

    response = await call_next(request)

    # 為歷史查詢 API 加上快取標頭
    if "/history" in request.url.path:
        response.headers["Cache-Control"] = "public, max-age=30"  # 快取 30 秒

    return response

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


from utils.db import init_db_pool, close_db_pool

@app.on_event("startup")
def startup_event():
    """應用程式啟動時初始化資料庫連線池"""
    init_db_pool()

@app.on_event("shutdown")
def shutdown_event():
    """應用程式關閉時釋放資料庫連線池"""
    close_db_pool()


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