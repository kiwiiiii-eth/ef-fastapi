#!/bin/bash
# FastAPI VPP 快速啟動腳本

echo "╔═══════════════════════════════════════════════════════════════════════════════╗"
echo "║                     FastAPI VPP 系統啟動中...                                   ║"
echo "╚═══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# 檢查是否安裝依賴
if ! python -c "import fastapi" 2>/dev/null; then
    echo "⚠️  檢測到缺少依賴，正在安裝..."
    pip install -r requirements.txt
    echo ""
fi

# 顯示啟動資訊
echo "🚀 啟動 FastAPI 開發伺服器..."
echo "📍 位置: $(pwd)"
echo "🌐 訪問地址:"
echo "   - 首頁: http://localhost:8000/"
echo "   - API 文檔 (Swagger): http://localhost:8000/docs"
echo "   - API 文檔 (ReDoc): http://localhost:8000/redoc"
echo "   - 健康檢查: http://localhost:8000/health"
echo ""
echo "💡 提示: 按 Ctrl+C 停止伺服器"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 啟動應用
python main.py