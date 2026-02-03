"""
資料庫模型定義
定義各種數據表的 SQL 建立語句和操作方法
"""


class SolarDataModel:
    """太陽能數據模型"""

    # 建表 SQL
    CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS solar_data (
        id SERIAL PRIMARY KEY,
        site_id VARCHAR(20) NOT NULL,
        datetime TIMESTAMP NOT NULL,
        daily_generation NUMERIC(10,2),
        solar_radiation NUMERIC(10,2),
        ac_avg_voltage NUMERIC(10,2),
        ac_total_power NUMERIC(10,2),
        ac_total_current NUMERIC(10,2),
        dc_avg_voltage NUMERIC(10,2),
        dc_total_power NUMERIC(10,2),
        dc_total_current NUMERIC(10,2),
        module_temperature NUMERIC(10,2),
        total_accumulated_generation NUMERIC(15,2),
        co2_reduction NUMERIC(15,3),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(site_id, datetime)
    );
    """

    # 建立索引 SQL
    CREATE_INDEX_SQL = [
        "CREATE INDEX IF NOT EXISTS idx_solar_site_datetime ON solar_data(site_id, datetime DESC);",
        "CREATE INDEX IF NOT EXISTS idx_solar_datetime ON solar_data(datetime DESC);"
    ]

    # 插入數據 SQL（使用 ON CONFLICT DO NOTHING 避免重複）
    INSERT_SQL = """
    INSERT INTO solar_data (
        site_id, datetime, daily_generation, solar_radiation,
        ac_avg_voltage, ac_total_power, ac_total_current,
        dc_avg_voltage, dc_total_power, dc_total_current,
        module_temperature, total_accumulated_generation, co2_reduction
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    ) ON CONFLICT (site_id, datetime) DO NOTHING;
    """

    # 查詢最新數據
    SELECT_LATEST_SQL = """
    SELECT * FROM solar_data
    WHERE site_id = %s
    ORDER BY datetime DESC
    LIMIT 1;
    """

    # 查詢所有場站最新數據
    SELECT_ALL_LATEST_SQL = """
    SELECT DISTINCT ON (site_id) *
    FROM solar_data
    ORDER BY site_id, datetime DESC;
    """

    # 查詢歷史數據
    SELECT_HISTORY_SQL = """
    SELECT * FROM solar_data
    WHERE site_id = %s
    AND datetime BETWEEN %s AND %s
    ORDER BY datetime DESC
    LIMIT %s;
    """


class LoadDataModel:
    """負載數據模型"""

    # 建表 SQL
    CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS load_data (
        id SERIAL PRIMARY KEY,
        site_id VARCHAR(20) NOT NULL,
        datetime TIMESTAMP NOT NULL,
        load_value NUMERIC(10,2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(site_id, datetime)
    );
    """

    # 建立索引 SQL
    CREATE_INDEX_SQL = [
        "CREATE INDEX IF NOT EXISTS idx_load_site_datetime ON load_data(site_id, datetime DESC);",
        "CREATE INDEX IF NOT EXISTS idx_load_datetime ON load_data(datetime DESC);"
    ]

    # 插入數據 SQL
    INSERT_SQL = """
    INSERT INTO load_data (site_id, datetime, load_value)
    VALUES (%s, %s, %s)
    ON CONFLICT (site_id, datetime) DO NOTHING;
    """

    # 查詢最新數據
    SELECT_LATEST_SQL = """
    SELECT * FROM load_data
    WHERE site_id = %s
    ORDER BY datetime DESC
    LIMIT 1;
    """

    # 查詢所有場站最新數據
    SELECT_ALL_LATEST_SQL = """
    SELECT DISTINCT ON (site_id) *
    FROM load_data
    ORDER BY site_id, datetime DESC;
    """

    # 查詢歷史數據
    SELECT_HISTORY_SQL = """
    SELECT * FROM load_data
    WHERE site_id = %s
    AND datetime BETWEEN %s AND %s
    ORDER BY datetime DESC
    LIMIT %s;
    """


class StorageDataModel:
    """儲能數據模型（預留）"""

    # 建表 SQL
    CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS storage_data (
        id SERIAL PRIMARY KEY,
        site_id VARCHAR(20) NOT NULL,
        datetime TIMESTAMP NOT NULL,
        soc NUMERIC(5,2),
        voltage NUMERIC(10,2),
        current NUMERIC(10,2),
        power NUMERIC(10,2),
        temperature NUMERIC(5,2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(site_id, datetime)
    );
    """

    # 建立索引 SQL
    CREATE_INDEX_SQL = [
        "CREATE INDEX IF NOT EXISTS idx_storage_site_datetime ON storage_data(site_id, datetime DESC);",
        "CREATE INDEX IF NOT EXISTS idx_storage_datetime ON storage_data(datetime DESC);"
    ]


class TaipowerReserveModel:
    """台電備轉容量資料模型"""

    # 建表 SQL
    CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS taipower_reserve_data (
        id SERIAL PRIMARY KEY,
        tran_date DATE NOT NULL,
        tran_hour INTEGER NOT NULL,

        -- 即時備轉 (SR - Spinning Reserve)
        sr_bid NUMERIC(10,2),
        sr_bid_qse NUMERIC(10,2),
        sr_bid_nontrade NUMERIC(10,2),
        sr_price NUMERIC(10,2),
        sr_perf_price_1 NUMERIC(10,2),
        sr_perf_price_2 NUMERIC(10,2),
        sr_perf_price_3 NUMERIC(10,2),

        -- 補充備轉 (SUP - Supplemental Reserve)
        sup_bid NUMERIC(10,2),
        sup_bid_qse NUMERIC(10,2),
        sup_bid_nontrade NUMERIC(10,2),
        sup_price NUMERIC(10,2),

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(tran_date, tran_hour)
    );
    """

    # 建立索引 SQL
    CREATE_INDEX_SQL = [
        "CREATE INDEX IF NOT EXISTS idx_taipower_date ON taipower_reserve_data(tran_date DESC);",
        "CREATE INDEX IF NOT EXISTS idx_taipower_date_hour ON taipower_reserve_data(tran_date DESC, tran_hour);"
    ]

    # 插入或更新數據 SQL (策略 B: DO UPDATE)
    UPSERT_SQL = """
    INSERT INTO taipower_reserve_data (
        tran_date, tran_hour,
        sr_bid, sr_bid_qse, sr_bid_nontrade, sr_price,
        sr_perf_price_1, sr_perf_price_2, sr_perf_price_3,
        sup_bid, sup_bid_qse, sup_bid_nontrade, sup_price
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    ON CONFLICT (tran_date, tran_hour)
    DO UPDATE SET
        sr_bid = EXCLUDED.sr_bid,
        sr_bid_qse = EXCLUDED.sr_bid_qse,
        sr_bid_nontrade = EXCLUDED.sr_bid_nontrade,
        sr_price = EXCLUDED.sr_price,
        sr_perf_price_1 = EXCLUDED.sr_perf_price_1,
        sr_perf_price_2 = EXCLUDED.sr_perf_price_2,
        sr_perf_price_3 = EXCLUDED.sr_perf_price_3,
        sup_bid = EXCLUDED.sup_bid,
        sup_bid_qse = EXCLUDED.sup_bid_qse,
        sup_bid_nontrade = EXCLUDED.sup_bid_nontrade,
        sup_price = EXCLUDED.sup_price,
        updated_at = CURRENT_TIMESTAMP;
    """

    # 查詢最新一天的數據 (24筆)
    SELECT_LATEST_DAY_SQL = """
    SELECT * FROM taipower_reserve_data
    WHERE tran_date = (SELECT MAX(tran_date) FROM taipower_reserve_data)
    ORDER BY tran_hour ASC;
    """

    # 查詢特定日期的數據
    SELECT_BY_DATE_SQL = """
    SELECT * FROM taipower_reserve_data
    WHERE tran_date = %s
    ORDER BY tran_hour ASC;
    """

    # 查詢歷史數據
    SELECT_HISTORY_SQL = """
    SELECT * FROM taipower_reserve_data
    WHERE tran_date BETWEEN %s AND %s
    ORDER BY tran_date DESC, tran_hour ASC
    LIMIT %s;
    """

    # 查詢特定日期統計資訊
    SELECT_STATISTICS_SQL = """
    SELECT
        tran_date,
        AVG(sr_price) as avg_sr_price,
        MAX(sr_price) as max_sr_price,
        MIN(sr_price) as min_sr_price,
        AVG(sup_price) as avg_sup_price,
        MAX(sup_price) as max_sup_price,
        MIN(sup_price) as min_sup_price,
        SUM(sr_bid + sr_bid_qse + sr_bid_nontrade) as total_sr_capacity,
        SUM(sup_bid + sup_bid_qse + sup_bid_nontrade) as total_sup_capacity
    FROM taipower_reserve_data
    WHERE tran_date = %s
    GROUP BY tran_date;
    """

    # 查詢特定日期特定時段的數據
    SELECT_BY_DATE_HOUR_SQL = """
    SELECT * FROM taipower_reserve_data
    WHERE tran_date = %s AND tran_hour = %s;
    """