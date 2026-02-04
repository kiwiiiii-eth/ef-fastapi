"""
資料庫工具模組
提供資料庫連接和操作的工具函數（FastAPI 版本 - 連線池版）
"""
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from config import Config
from typing import Optional, List, Dict, Any
import logging

# 設定日誌
logger = logging.getLogger(__name__)

# 全域連線池變數
db_pool = None


def init_db_pool():
    """初始化資料庫連線池"""
    global db_pool
    try:
        db_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=Config.DB_POOL_SIZE if hasattr(Config, 'DB_POOL_SIZE') else 20,
            host=Config.POSTGRES_HOST,
            user=Config.POSTGRES_USER,
            password=Config.POSTGRES_PASSWORD,
            dbname=Config.POSTGRES_DATABASE,
            port=Config.POSTGRES_PORT,
            connect_timeout=10,  # 連線超時 10 秒
            options='-c statement_timeout=30000'  # SQL 查詢超時 30 秒
        )
        logger.info("資料庫連線池初始化成功")
    except Exception as e:
        logger.error(f"資料庫連線池初始化失敗: {e}")
        raise e


def close_db_pool():
    """關閉資料庫連線池"""
    global db_pool
    if db_pool:
        db_pool.closeall()
        logger.info("資料庫連線池已關閉")


@contextmanager
def get_db_connection():
    """
    從連線池取得連線 (Context Manager)
    使用方式:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            ...
    """
    global db_pool
    if db_pool is None:
        # 如果連線池尚未初始化 (例如在測試或腳本中)，嘗試初始化
        init_db_pool()

    conn = None
    try:
        conn = db_pool.getconn()
        yield conn
    except Exception as e:
        logger.error(f"取得資料庫連線失敗: {e}")
        raise e
    finally:
        if conn:
            db_pool.putconn(conn)


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
    with get_db_connection() as conn:
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
            logger.error(f"SQL 執行失敗: {e}\nQuery: {query}\nParams: {params}")
            raise e

        finally:
            cursor.close()


def execute_batch(query: str, data_list: List[tuple]) -> int:
    """
    批次執行 SQL 插入

    Args:
        query (str): SQL 插入語句
        data_list (list): 要插入的數據列表

    Returns:
        int: 成功插入的筆數
    """
    with get_db_connection() as conn:
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
            logger.error(f"批次執行失敗: {e}")
            raise e

        finally:
            cursor.close()



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