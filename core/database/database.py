import datetime
import os
import random
import sqlite3

class Database():
    def __init__(self, db_filename="order_management.db"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, db_filename)
        # 建議在初始化時建立表格（如果不存在）
        self._create_tables()

    def _create_tables(self):
        """建立 commodity 和 order_list 表格（如果不存在）"""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            # 1. commodity 表格 (包含 category, product, price)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS commodity (
                    category TEXT NOT NULL,
                    product TEXT PRIMARY KEY,
                    price REAL NOT NULL
                );
            """)
            # 2. order_list 表格 (包含 order_id, 訂單細節, product_total, product_note)
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

    @staticmethod
    def generate_order_id() -> str:
        """生成唯一的訂單 ID"""
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        random_num = random.randint(1000, 9999)
        return f"OD{timestamp}{random_num}"

    def get_product_names_by_category(self, category):
        """回傳指定 category 下面所有 product 名稱（列表）"""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            sql = "SELECT product FROM commodity WHERE category = ?"
            cur.execute(sql, (category,))
            # 將 (('A',), ('B',)) 轉換為 ['A', 'B'] 列表
            results = [row[0] for row in cur.fetchall()]
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
    
    def add_order(self, cur, order_data):

    def get_all_orders(self, cur):

    def delete_order(self, cur, order_id):
