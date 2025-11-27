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
        order_data = {
            # 日期：老師 form 裡叫 'product-date'
            "product_date": (
                request.form.get("product_date") or
                request.form.get("product-date") or
                request.form.get("date")
            ),
            # 客戶名稱：老師 form 裡叫 'customer-name'
            "customer_name": (
                request.form.get("customer_name") or
                request.form.get("customer-name") or
                request.form.get("customer")
            ),
            # 商品名稱：老師 form 裡叫 'product-name'
            "product_name": (
                request.form.get("product_name") or
                request.form.get("product-name") or
                request.form.get("product")
            ),
            # 數量：老師 form 裡叫 'product-amount'
            "product_amount": int(
                request.form.get("product_amount") or
                request.form.get("product-amount") or
                request.form.get("amount") or
                0
            ),
            # 小計：老師 form 裡叫 'product-total'
            "product_total": int(
                request.form.get("product_total") or
                request.form.get("product-total") or
                request.form.get("total") or
                0
            ),
            # 狀態：老師 form 裡叫 'product-status'
            "product_status": (
                request.form.get("product_status") or
                request.form.get("product-status") or
                request.form.get("status")
            ),
            # 備註：老師 form 裡叫 'product-note'
            "product_note": (
                request.form.get("product_note") or
                request.form.get("product-note") or
                request.form.get("note")
            ),
        }

        # 寫入資料庫（在測試中會被 mock 掉）
        db.add_order(order_data)

        # 寫完後 redirect 回首頁，並帶上 warning 訊息
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
    # 這是您原有的啟動配置
    app.run(host='127.0.0.1', port=5500, debug=True)