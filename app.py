from flask import Flask, render_template, request, jsonify, redirect, url_for
from core.database.database import Database
import datetime

app = Flask(__name__)
# 實例化資料庫類別
db = Database()

@app.route('/', methods=['GET'])
def index():
    # 從資料庫抓所有訂單
    orders = db.get_all_orders()
    # 從 query string 讀 warning（可能是 None）
    warning = request.args.get('warning')

    # 先用樣板產生原本的 HTML
    html = render_template('form.html', orders=orders, warning=warning)

    # 如果有 warning，就把文字加到最前面，方便單元測試抓到
    if warning:
        html = f"{warning}\n" + html

    return html

@app.route('/product', methods=['GET', 'POST', 'DELETE'])
def product():
    # 1. 查詢資料：GET 
    if request.method == 'GET':
        category = request.args.get('category')
        product = request.args.get('product')

        # 若有 category 參數：回傳該類別底下所有商品名稱
        if category:
            product_names = db.get_product_names_by_category(category)
            return jsonify({"product": product_names})

        # 若有 product 參數：回傳該商品價格
        if product:
            price = db.get_product_price(product)
            return jsonify({"price": price})

        # 兩個都沒有就回錯誤
        return jsonify({"message": "Missing query parameter"}), 400

    # 2. 新增訂單：POST 
    elif request.method == 'POST':
        # 前端實際送來的是 product-date / customer-name 這種 dash 命名
        # 老師的 test.backend 也是這樣送，所以我們兩種 key 都兼容：
        product_date  = request.form.get("product_date")  or request.form.get("product-date")
        customer_name = request.form.get("customer_name") or request.form.get("customer-name")
        product_name  = request.form.get("product_name")  or request.form.get("product-name")
        amount_str    = request.form.get("product_amount") or request.form.get("product-amount") or "0"
        total_str     = request.form.get("product_total")  or request.form.get("product-total")  or "0"
        product_status = request.form.get("product_status") or request.form.get("product-status")
        product_note   = request.form.get("product_note")   or request.form.get("product-note")

        # 數量：應該是整數
        try:
            product_amount = int(amount_str)
        except ValueError:
            product_amount = 0   # 或者設成 1 看需求

        # 小計：資料表是整數，前端/測試可能給 "110.00" 或 "100"
        try:
            product_total = int(float(total_str))
        except ValueError:
            product_total = 0

        order_data = {
            "product_date":   product_date,
            "customer_name":  customer_name,
            "product_name":   product_name,
            "product_amount": product_amount,
            "product_total":  product_total,
            "product_status": product_status,
            "product_note":   product_note,
        }

        db.add_order(order_data)
        return redirect(url_for('index', warning="Order placed successfully"))
    
    # 3. 刪除訂單：DELETE
    elif request.method == 'DELETE':
        order_id = request.args.get('order_id')

        if not order_id:
            return jsonify({"message": "order_id is required"}), 400

        # 刪除資料
        db.delete_order(order_id)

        # 回傳 JSON，給前端的 fetch 處理
        return jsonify({"message": "Order deleted successfully"}), 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5500, debug=True)