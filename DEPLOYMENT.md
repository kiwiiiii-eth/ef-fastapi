# FastAPI VPP 部署指南

## 部署到 Zeabur

### 方法一：使用 Gunicorn + Uvicorn Workers（推薦）

1. **安裝額外依賴**

```bash
pip install gunicorn
```

2. **更新 requirements.txt**

在 `requirements.txt` 加入：
```
gunicorn==21.2.0
```

3. **建立啟動指令**

在 Zeabur 設定啟動指令：
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

參數說明：
- `-w 4`: 4 個 worker 程序
- `-k uvicorn.workers.UvicornWorker`: 使用 Uvicorn worker 類別
- `--bind 0.0.0.0:$PORT`: 綁定到所有介面和動態端口

### 方法二：直接使用 Uvicorn

在 Zeabur 設定啟動指令：
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## 環境變數配置

在 Zeabur 控制台設定以下環境變數：

### 必需變數

```env
# PostgreSQL 資料庫連線（Zeabur 會自動提供）
POSTGRES_HOST=<your_postgres_host>
POSTGRES_USER=<your_postgres_user>
POSTGRES_PASSWORD=<your_postgres_password>
POSTGRES_DATABASE=<your_postgres_database>
POSTGRES_PORT=<your_postgres_port>

# 應用程式端口（Zeabur 會自動設定）
PORT=8000
```

### 可選變數

```env
# 外部 API Token（若需要使用資料收集功能）
YIHONG_API_TOKEN=<your_api_token>
```

---

## 部署前檢查清單

- [ ] 確認 `requirements.txt` 包含所有依賴
- [ ] 確認 `runtime.txt` 指定 Python 版本
- [ ] 測試所有 API 端點能正常運作
- [ ] 確認資料庫連線正常
- [ ] 檢查環境變數是否正確設定

---

## 本地測試部署指令

### 開發模式

```bash
# 使用 uvicorn（自動重載）
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 或直接執行
python main.py
```

### 生產模式模擬

```bash
# 使用 Gunicorn + Uvicorn workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 使用 Uvicorn（無重載）
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 效能調校建議

### Worker 數量

根據 CPU 核心數調整：
```
workers = (CPU核心數 × 2) + 1
```

例如：2 核心 CPU 建議 5 個 workers

### Uvicorn 參數

```bash
uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --limit-concurrency 100 \
  --timeout-keep-alive 5
```

參數說明：
- `--workers`: Worker 程序數
- `--limit-concurrency`: 最大並發連線數
- `--timeout-keep-alive`: Keep-alive 超時時間（秒）

---

## 監控與日誌

### 查看應用程式日誌

Zeabur 控制台 → 服務 → 日誌

### 健康檢查端點

```bash
curl https://your-app.zeabur.app/health
```

回應：
```json
{
  "status": "healthy",
  "service": "VPP FastAPI"
}
```

---

## 常見問題排解

### 1. 應用程式無法啟動

**檢查項目：**
- 確認 Python 版本正確（3.11）
- 檢查依賴是否完整安裝
- 查看啟動日誌錯誤訊息

### 2. 資料庫連線失敗

**檢查項目：**
- 確認環境變數設定正確
- 檢查 PostgreSQL 服務是否運行
- 測試資料庫連線：
  ```bash
  python -c "from utils.db import get_db_connection; conn = get_db_connection(); print('✓ 連線成功')"
  ```

### 3. API 回應 500 錯誤

**檢查項目：**
- 查看詳細錯誤訊息（`/docs` 端點測試）
- 確認資料表是否存在
- 檢查 SQL 查詢語法

### 4. CORS 錯誤

**解決方法：**
- 在 `main.py` 中調整 `allow_origins`
- 生產環境建議設定具體域名：
  ```python
  allow_origins=["https://your-frontend-domain.com"]
  ```

---

## 遷移步驟（從 Flask 切換到 FastAPI）

### 1. 準備階段

```bash
# 備份現有 Flask 應用
cd /path/to/project
cp -r flask flask_backup

# 確認 FastAPI 版本測試通過
cd fastapi
python test_routes.py
```

### 2. 部署 FastAPI

在 Zeabur 建立新服務或更新現有服務：
- 指向 `fastapi/` 目錄
- 設定環境變數
- 設定啟動指令

### 3. 驗證部署

```bash
# 測試健康檢查
curl https://your-app.zeabur.app/health

# 測試 API 文檔
# 訪問 https://your-app.zeabur.app/docs

# 測試實際 API
curl https://your-app.zeabur.app/api/vpp/realdata
```

### 4. 切換流量

確認 FastAPI 正常運作後：
- 更新前端 API 端點（如果域名改變）
- 監控錯誤日誌
- 保留 Flask 版本作為備份

---

## 效能基準測試

### 使用 Apache Bench

```bash
# 安裝 ab
# macOS: brew install httpd
# Ubuntu: apt-get install apache2-utils

# 測試首頁
ab -n 1000 -c 10 http://localhost:8000/

# 測試 API 端點
ab -n 1000 -c 10 http://localhost:8000/api/vpp/realdata
```

### 預期效能

- **吞吐量**: 1000+ 請求/秒（簡單查詢）
- **延遲**: < 50ms（本地資料庫）
- **並發**: 支援 100+ 並發連線

---

## 備份與還原

### 備份策略

1. **程式碼備份**: 使用 Git 版本控制
2. **資料庫備份**: 定期匯出 PostgreSQL
   ```bash
   pg_dump -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DATABASE > backup.sql
   ```

### 還原 Flask 版本

如果需要回退：
```bash
# 切換回 Flask 目錄
cd flask

# 啟動 Flask 應用
gunicorn app:app --bind 0.0.0.0:$PORT
```

---

## 更新依賴

定期更新依賴套件：

```bash
# 列出過期套件
pip list --outdated

# 更新特定套件
pip install --upgrade fastapi uvicorn

# 重新生成 requirements.txt
pip freeze > requirements.txt
```

**注意**: 主要版本更新前請先在本地測試！

---

## 聯絡支援

遇到問題請檢查：
1. FastAPI 官方文檔: https://fastapi.tiangolo.com/
2. Zeabur 文檔: https://zeabur.com/docs
3. 專案 README.md