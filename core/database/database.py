import datetime
import os
import random
import sqlite3

class Database():
    _initialized = False

    def __init__(self, db_filename="order_management.db"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, db_filename)

        # 只初始化「自己用的 order_management.db」，不要動 test_order_management.db
        if not Database._initialized and db_filename == "order_management.db":
            self._create_tables()
            self._initialize_data()
            Database._initialized = True

    def _create_tables(self):
        """建立 commodity 和 order_list 表格（如果不存在）"""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            # 1. commodity 表格
            cur.execute("""
                CREATE TABLE IF NOT EXISTS commodity (
                    category TEXT NOT NULL,
                    product TEXT PRIMARY KEY,
                    price REAL NOT NULL
                );
            """)
            # 2. order_list 表格
            cur.execute("""
                CREATE TABLE IF NOT EXISTS order_list (
                    order_id TEXT PRIMARY KEY,
                    product_date TEXT NOT NULL,
                    customer_name TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    product_amount INTEGER NOT NULL,
                    product_total REAL NOT NULL,
                    product_status TEXT NOT NULL,
                    product_note TEXT
                );
            """)
            conn.commit()

    def _initialize_data(self):
        """插入測試所需的商品和訂單數據（確保測試通過）"""
        TEST_COMMODITY = [
            ('飯類', '咖哩飯', 90.0), 
            ('飯類', '排骨飯', 120.0),
            ('麵食', '牛肉麵', 150.0),
        ]

        TEST_ORDERS = []
        for i in range(1, 11):
            TEST_ORDERS.append((
                f"OD20240101000{i}",  # order_id
                '2024-01-01',        # date
                f"客戶{i}",           # customer_name
                '咖哩飯',             # product
                i,                   # amount
                90.0 * i,            # total
                '未付款',             # status
                f"備註{i}"            # note
            ))

        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()

            # A. commodity 不用改
            sql_comm = """
                INSERT OR IGNORE INTO commodity (category, product, price)
                VALUES (?, ?, ?)
            """
            cur.executemany(sql_comm, TEST_COMMODITY)

            # B. 這裡欄位名稱一定要跟 .schema order_list 一樣
            sql_order = """
                INSERT OR IGNORE INTO order_list (
                    order_id,
                    date,
                    customer_name,
                    product,
                    amount,
                    total,
                    status,
                    note
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            cur.executemany(sql_order, TEST_ORDERS)

            conn.commit()
            
    @staticmethod
    def generate_order_id() -> str:
        """生成唯一的訂單 ID"""
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        random_num = random.randint(1000, 9999)
        return f"OD{timestamp}{random_num}"

    def get_product_names_by_category(self, category):
        """回傳指定 category 下面所有 product 名稱（老師期待 list of tuple）"""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            sql = "SELECT product FROM commodity WHERE category = ?"
            cur.execute(sql, (category,))
            results = cur.fetchall()  
        return results
       
    def get_product_price(self, product):
        """根據 product 名稱查詢單價"""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            sql = "SELECT price FROM commodity WHERE product = ?"
            cur.execute(sql, (product,))
            result = cur.fetchone()
        # 如果找到，回傳價格（float）；否則回傳 None
        return result[0] if result else None
    
    def add_order(self, order_data):
        """將訂單資料字典寫入 order_list 資料表"""

        if 'order_id' not in order_data:
            order_data['order_id'] = self.generate_order_id()

        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()

            # 注意：這裡的欄位名稱要完全符合 .schema order_list
            sql = """
                INSERT INTO order_list (
                    order_id,
                    date,
                    customer_name,
                    product,
                    amount,
                    total,
                    status,
                    note
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            values = (
                order_data['order_id'],
                # dict 裡的 key 仍然叫 product_date，寫入到欄位 date 沒關係
                order_data['product_date'],
                order_data['customer_name'],
                order_data['product_name'],    # 寫入到欄位 product
                order_data['product_amount'],  # 寫入到欄位 amount
                order_data['product_total'],   # 寫入到欄位 total
                order_data['product_status'],  # 寫入到欄位 status
                order_data.get('product_note')
            )
            cur.execute(sql, values)
            conn.commit()

    def delete_order(self, order_id):
        """根據 order_id 刪除特定訂單"""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            sql = "DELETE FROM order_list WHERE order_id = ?"
            cur.execute(sql, (order_id,))
            deleted_count = cur.rowcount
            conn.commit()
        return deleted_count > 0

    def get_all_orders(self):
        """
        取得所有訂單，並 JOIN commodity 查回 price 欄位。
        每列格式：
        (order_id, date, customer_name,
         product, price, amount,
         total, status, note)
        """
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            sql = """
                SELECT
                    o.order_id,
                    o.date,
                    o.customer_name,
                    o.product,
                    c.price,      -- index 4
                    o.amount,     -- index 5
                    o.total,      -- index 6
                    o.status,
                    o.note
                FROM order_list AS o
                LEFT JOIN commodity AS c
                    ON o.product = c.product
            """
            cur.execute(sql)
            orders_list = cur.fetchall()
        return orders_list
    