from flask import Flask, render_template, request, jsonify, redirect, url_for
from core.database.database import Database

app = Flask(__name__)
db = Database()

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
            "product_date":   request.form.get("product_date"),
            "customer_name":  request.form.get("customer_name"),
            "product_name":   request.form.get("product_name"),
            "product_amount": request.form.get("product_amount"),
            "product_total":  request.form.get("product_total"),
            "product_status": request.form.get("product_status"),
            "product_note":   request.form.get("product_note"),
        }

        # 寫入資料庫
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