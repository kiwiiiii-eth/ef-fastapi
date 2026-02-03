"""
FastAPI 路由測試腳本
驗證所有端點是否正確註冊
"""
from main import app

def test_routes():
    """測試所有路由是否正確註冊"""
    print("=" * 80)
    print("FastAPI VPP 系統路由測試")
    print("=" * 80)

    # 預期的端點
    expected_endpoints = {
        "VPP 查詢端點": [
            ("GET", "/api/vpp/realdata"),
            ("GET", "/api/vpp/realdata/{site_id}"),
            ("GET", "/api/vpp/solar/latest"),
            ("GET", "/api/vpp/solar/history"),
            ("GET", "/api/vpp/load/latest"),
            ("GET", "/api/vpp/load/history"),
            ("GET", "/api/vpp/summary"),
        ],
        "台電資料端點": [
            ("GET", "/api/taipower/reserve/latest"),
            ("GET", "/api/taipower/reserve/date"),
            ("GET", "/api/taipower/reserve/history"),
            ("GET", "/api/taipower/reserve/statistics"),
            ("GET", "/api/taipower/reserve/hour"),
        ],
        "樹莓派上傳端點": [
            ("POST", "/api/upload"),
        ],
        "系統端點": [
            ("GET", "/"),
            ("GET", "/health"),
        ]
    }

    # 取得所有已註冊的路由
    registered_routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            for method in route.methods:
                if method not in ['HEAD', 'OPTIONS']:  # 忽略 HEAD 和 OPTIONS
                    registered_routes.append((method, route.path))

    # 檢查每個預期的端點
    total_expected = 0
    total_found = 0

    for category, endpoints in expected_endpoints.items():
        print(f"\n【{category}】")
        for method, path in endpoints:
            total_expected += 1
            if (method, path) in registered_routes:
                print(f"  ✓ {method:6} {path}")
                total_found += 1
            else:
                print(f"  ✗ {method:6} {path} - 未找到")

    # 檢查是否有額外的端點
    print(f"\n【其他系統端點】")
    for method, path in registered_routes:
        is_expected = False
        for endpoints in expected_endpoints.values():
            if (method, path) in endpoints:
                is_expected = True
                break
        if not is_expected and not path.startswith(("/openapi", "/docs", "/redoc")):
            print(f"  ℹ {method:6} {path} - 額外端點")

    # 總結
    print("\n" + "=" * 80)
    print(f"測試結果：{total_found}/{total_expected} 個端點正確註冊")

    if total_found == total_expected:
        print("✓ 所有端點測試通過！")
        return True
    else:
        print("✗ 部分端點缺失，請檢查路由配置")
        return False


if __name__ == "__main__":
    success = test_routes()
    exit(0 if success else 1)