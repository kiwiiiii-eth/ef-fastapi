# FastAPI 虛擬電廠 (VPP) API

這是從 Flask 轉換到 FastAPI 的虛擬電廠系統後端 API。

## 功能特色

- ⚡ **FastAPI 框架** - 高效能、自動文檔生成
- 🔄 **同步資料庫** - 使用 psycopg2 連接 PostgreSQL
- 📊 **完整 API** - 太陽能、負載、台電備轉資料查詢
- 📝 **自動驗證** - Pydantic 資料模型自動驗證請求
- 🌐 **CORS 支援** - 跨域請求支援
- 📚 **自動文檔** - Swagger UI 和 ReDoc

## 專案結構

```
fastapi/
├── main.py                    # FastAPI 應用入口
├── config.py                  # 配置管理
├── models.py                  # SQL 查詢定義
├── requirements.txt           # Python 依賴
├── runtime.txt               # Python 版本
├── .env.example              # 環境變數範例
│
├── routers/                  # API 路由
│   ├── vpp.py               # VPP 查詢端點（8個）
│   ├── taipower.py          # 台電查詢端點（5個）
│   └── upload.py            # 樹莓派上傳端點（1個）
│
├── schemas/                  # Pydantic 資料模型
│   ├── solar.py
│   ├── load.py
│   ├── taipower.py
│   └── upload.py
│
└── utils/                    # 工具函數
    └── db.py                # 資料庫連接
```

## 快速開始

### 1. 安裝依賴

```bash
cd fastapi
pip install -r requirements.txt
```

### 2. 配置環境變數

```bash
cp .env.example .env
# 編輯 .env 填入正確的資料庫連線資訊
```

### 3. 啟動開發伺服器

```bash
# 方式 1: 直接執行
python main.py

# 方式 2: 使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 查看 API 文檔

啟動後訪問：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 健康檢查: http://localhost:8000/health

## API 端點列表

### VPP 查詢 (8 個端點)

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/vpp/realdata` | GET | 查詢所有場站即時數據 |
| `/api/vpp/realdata/{site_id}` | GET | 查詢特定場站即時數據 |
| `/api/vpp/solar/latest` | GET | 查詢最新太陽能數據 |
| `/api/vpp/solar/history` | GET | 查詢太陽能歷史數據 |
| `/api/vpp/load/latest` | GET | 查詢最新負載數據 |
| `/api/vpp/load/history` | GET | 查詢負載歷史數據 |
| `/api/vpp/summary` | GET | 查詢彙總統計資訊 |

### 台電資料 (5 個端點)

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/taipower/reserve/latest` | GET | 查詢最新備轉資料 |
| `/api/taipower/reserve/date` | GET | 查詢特定日期備轉資料 |
| `/api/taipower/reserve/history` | GET | 查詢歷史備轉資料 |
| `/api/taipower/reserve/statistics` | GET | 查詢統計資訊 |
| `/api/taipower/reserve/hour` | GET | 查詢特定時段資料 |

### 樹莓派上傳 (1 個端點)

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/upload` | POST | 樹莓派數據上傳 |

## 部署到 Zeabur

### 使用 Uvicorn + Gunicorn

```bash
# 安裝 gunicorn
pip install gunicorn

# 啟動（生產環境）
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

### 環境變數設定

在 Zeabur 設定以下環境變數：
- `POSTGRES_HOST`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DATABASE`
- `POSTGRES_PORT`

## Flask vs FastAPI 比較

| 項目 | Flask | FastAPI |
|------|-------|---------|
| 框架版本 | 3.0.0 | 0.115.0 |
| 伺服器 | Gunicorn | Uvicorn |
| 資料驗證 | 手動 | Pydantic 自動 |
| API 文檔 | 手寫 | 自動生成 |
| 類型提示 | 可選 | 強制 |
| 效能 | 標準 | 高效能 |

## 測試 API

### 使用 curl

```bash
# 查詢即時數據
curl http://localhost:8000/api/vpp/realdata

# 查詢特定場站
curl http://localhost:8000/api/vpp/realdata/north

# 查詢太陽能歷史數據
curl "http://localhost:8000/api/vpp/solar/history?site_id=north&start_date=2026-01-28&limit=100"

# 查詢台電備轉資料
curl "http://localhost:8000/api/taipower/reserve/date?date=2026-02-03"

# 上傳數據
curl -X POST http://localhost:8000/api/upload \
  -H "Content-Type: application/json" \
  -d '{"device_id": "pi_001", "value": 24.5, "timestamp": "2026-02-03 14:30:05"}'
```

## 注意事項

1. **排程功能未包含** - 依照需求，資料收集排程器未轉換
2. **保持原有路徑** - 所有 API 端點路徑與 Flask 版本完全相同
3. **錯誤格式相同** - 錯誤回應格式保持與原 Flask 版本一致
4. **同步資料庫** - 使用 psycopg2 同步連接，未來可升級為 asyncpg 異步

## 技術棧

- **FastAPI** 0.115.0 - Web 框架
- **Uvicorn** 0.32.0 - ASGI 伺服器
- **Pydantic** 2.9.2 - 資料驗證
- **psycopg2** 2.9.9 - PostgreSQL 驅動
- **Python** 3.11

## 授權

此專案為內部使用。