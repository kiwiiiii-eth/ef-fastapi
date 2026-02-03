"""
資料庫工具模組
提供資料庫連接和操作的工具函數（FastAPI 版本）
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config
from typing import Optional, List, Dict, Any


def get_db_connection():
    """
    建立資料庫連接

    Returns:
        psycopg2.connection: PostgreSQL 資料庫連接物件
    """
    conn = psycopg2.connect(
        host=Config.POSTGRES_HOST,
        user=Config.POSTGRES_USER,
        password=Config.POSTGRES_PASSWORD,
        dbname=Config.POSTGRES_DATABASE,
        port=Config.POSTGRES_PORT
    )
    return conn


def execute_query(query: str, params: Optional[tuple] = None, fetch: bool = False, fetch_one: bool = False) -> Optional[Any]:
    """
    執行 SQL 查詢

    Args:
        query (str): SQL 查詢語句
        params (tuple): 查詢參數
        fetch (bool): 是否返回查詢結果（多筆）
        fetch_one (bool): 是否返回單筆查詢結果

    Returns:
        list/dict/None: 查詢結果或 None
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(query, params)

        if fetch:
            result = cursor.fetchall()
        elif fetch_one:
            result = cursor.fetchone()
        else:
            result = None

        conn.commit()
        return result

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()


def execute_batch(query: str, data_list: List[tuple]) -> int:
    """
    批次執行 SQL 插入

    Args:
        query (str): SQL 插入語句
        data_list (list): 要插入的數據列表

    Returns:
        int: 成功插入的筆數
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    success_count = 0

    try:
        for data in data_list:
            try:
                cursor.execute(query, data)
                success_count += cursor.rowcount
            except psycopg2.IntegrityError:
                # 忽略重複數據（UNIQUE 約束衝突）
                conn.rollback()
                continue

        conn.commit()
        return success_count

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()


def row_to_dict(row) -> Optional[Dict[str, Any]]:
    """
    將查詢結果轉換為字典（處理 RealDictRow）

    Args:
        row: 資料庫查詢結果行

    Returns:
        dict: 轉換後的字典
    """
    if row is None:
        return None

    result = {}
    for key, value in row.items():
        # 處理日期時間格式
        if hasattr(value, 'isoformat'):
            result[key] = value.isoformat()
        # 處理 Decimal 類型
        elif hasattr(value, '__float__'):
            result[key] = float(value)
        else:
            result[key] = value

    return result