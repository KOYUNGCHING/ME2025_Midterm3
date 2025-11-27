// 取得 DOM 元素
const categorySelect = document.getElementById('category');          // 商品種類
const productSelect  = document.getElementById('product_name');      // 商品名稱
const amountInput    = document.getElementById('product_amount');    // 數量
const priceInput     = document.getElementById('product_price');     // 單價 input
const totalInput     = document.getElementById('product_total');     // 小計 input
const orderForm      = document.getElementById('order-form');        // 表單
const modal          = document.getElementById('addModal');          // Modal (新增訂單視窗)

// Modal 開啟 / 關閉
function open_input_table() {
    if (modal) {
        modal.style.display = "block";
    }
    resetFields();   // 每次開啟時重設欄位
}

function close_input_table() {
    if (modal) {
        modal.style.display = "none";
    }
}

// 重設欄位
function resetFields() {
    // 商品名稱下拉選單恢復預設
    if (productSelect) {
        productSelect.innerHTML = '<option value="" disabled selected>請選擇商品</option>';
    }

    // 單價歸 0
    if (priceInput) {
        priceInput.value = '0.00';
    }

    // 小計歸 0
    if (totalInput) {
        totalInput.value = '0.00';
    }

    // 數量至少為 1
    if (amountInput) {
        if (!amountInput.value || parseInt(amountInput.value) < 1) {
            amountInput.value = 1;
        }
    }
}

// 選擇「商品種類」後：向後端拿商品名稱列表
async function selectCategory() {
    if (!categorySelect || !productSelect) return;

    const category = categorySelect.value;
    if (!category) {
        resetFields();
        return;
    }

    // 更新 UI：顯示載入中
    productSelect.innerHTML = '<option value="" disabled selected>載入中...</option>';
    if (priceInput) priceInput.value = '0.00';
    if (totalInput) totalInput.value = '0.00';

    try {
        const response = await fetch(`/product?category=${encodeURIComponent(category)}`);
        if (!response.ok) {
            throw new Error(`HTTP 錯誤! 狀態碼: ${response.status}`);
        }

        const data = await response.json();
        const products = data.product || [];

        // 填入商品名稱選項
        productSelect.innerHTML = '<option value="" disabled selected>請選擇商品</option>';
        products.forEach((product) => {
            const option = document.createElement('option');
            option.value = product;
            option.textContent = product;
            productSelect.appendChild(option);
        });
    } catch (error) {
        console.error("Fetch product list by category failed:", error);
        alert(`無法載入商品列表: ${error.message}`);
        productSelect.innerHTML = '<option value="" disabled selected>載入失敗</option>';
    }
}

// 選擇「商品名稱」後：向後端拿單價
async function selectProduct() {
    if (!productSelect || !priceInput || !totalInput) return;

    const product = productSelect.value;
    if (!product) {
        priceInput.value = '0.00';
        totalInput.value = '0.00';
        return;
    }

    try {
        const response = await fetch(`/product?product=${encodeURIComponent(product)}`);
        if (!response.ok) {
            throw new Error(`HTTP 錯誤! 狀態碼: ${response.status}`);
        }

        const data = await response.json();
        const price = data.price || 0;

        // 更新單價
        priceInput.value = parseFloat(price).toFixed(2);

        // 重新計算小計
        countTotal();
    } catch (error) {
        console.error("Fetch product price failed:", error);
        alert(`無法載入商品價格: ${error.message}`);
        priceInput.value = '0.00';
        totalInput.value = '0.00';
    }
}

// 計算小計：單價 * 數量
function countTotal() {
    if (!priceInput || !amountInput || !totalInput) return;

    const priceText = priceInput.value;
    let price  = parseFloat(priceText) || 0;

    let amount = parseInt(amountInput.value) || 0;
    if (amount <= 0) {
        amount = 1;
        amountInput.value = 1;
    }

    const total = price * amount;
    totalInput.value = total.toFixed(2);
}

// 表單送出：用 fetch POST /product
async function handleSubmit(event) {
    // 防止瀏覽器預設提交行為（避免整頁刷新）
    event.preventDefault();

    if (!orderForm) return;

    // 確保小計最新
    countTotal();

    const formData = new FormData(orderForm);

    // 檢查必填欄位：商品名稱
    if (!formData.get('product_name')) {
        alert('請先選擇商品名稱！');
        return;
    }

    // 確保狀態有值（預設未付款）
    if (!formData.get('product_status')) {
        formData.set('product_status', '未付款');
    }

    try {
        const response = await fetch('/product', {
            method: 'POST',
            body: formData,
        });

        // Flask redirect 預設 status code=302
        if (response.status === 302 || response.ok) {
            if (response.redirected) {
                window.location.href = response.url;
            } else {
                window.location.assign('/');
            }
        } else {
            const errorText = await response.text();
            throw new Error(`提交訂單失敗: ${response.status} - ${errorText}`);
        }
    } catch (error) {
        console.error("Order submission failed:", error);
        alert(`提交訂單失敗，請檢查網路或欄位資料: ${error.message}`);
    }
}

// 刪除訂單
function delete_data(value) {
    if (!value) {
        alert("缺少 order_id，無法刪除");
        return;
    }

    if (!confirm("確定要刪除這筆訂單嗎？")) {
        return;
    }

    fetch(`/product?order_id=${encodeURIComponent(value)}`, {
        method: "DELETE",
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error("伺服器回傳錯誤");
            }
            return response.json();
        })
        .then((result) => {
            console.log(result);
            // 重新整理頁面，讓列表更新
            location.assign('/');
        })
        .catch((error) => {
            console.error("發生錯誤：", error);
            alert("刪除失敗，請稍後再試");
        });
}

// 設定日期欄位為今天
function setToday() {
    const dateInput = document.getElementById("product_date");
    if (!dateInput) return;

    const today = new Date().toISOString().split("T")[0];
    dateInput.value = today;
}

// 綁定事件
window.addEventListener("DOMContentLoaded", () => {
    // 日期預設今天
    setToday();

    // 重設欄位初始狀態
    resetFields();

    // 商品種類變更 → 更新商品名稱
    if (categorySelect) {
        categorySelect.addEventListener('change', selectCategory);
    }

    // 商品名稱變更 → 更新單價 + 小計
    if (productSelect) {
        productSelect.addEventListener('change', selectProduct);
    }

    // 數量變更 → 重新計算小計
    if (amountInput) {
        amountInput.addEventListener('change', countTotal);
        amountInput.addEventListener('input', countTotal);
    }

    // 表單送出 → 自己用 fetch POST
    if (orderForm) {
        orderForm.addEventListener('submit', handleSubmit);
    }
});