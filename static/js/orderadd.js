// 1. 取得 DOM 元素
const categorySelect = document.getElementById('category');
const productSelect = document.getElementById('product_name'); // product_name 欄位
const amountInput = document.getElementById('product_amount'); // 數量欄位
const priceDisplay = document.getElementById('price_display'); // 顯示單價的元素
const totalInput = document.getElementById('product_total');  // 存放總價的隱藏欄位 
const orderForm = document.getElementById('addOrderForm'); // 假設表單的 ID

// 開啟與關閉Modal
function open_input_table() {
    document.getElementById("addModal").style.display = "block";
    // 每次開啟時，確保單價和總價歸零或重設
    resetFields();
}
function close_input_table() {
    document.getElementById("addModal").style.display = "none";
}

// 其他輔助函數：重設欄位
function resetFields() {
    // 重設商品名稱下拉選單
    productSelect.innerHTML = '<option value="" disabled selected>請選擇商品</option>';
    // 重設單價顯示
    priceDisplay.textContent = '0.00'; 
    // 重設總價隱藏欄位
    totalInput.value = 0.00;
    // 確保數量不小於1
    if (amountInput.value < 1) {
        amountInput.value = 1;
    }
}



// 1. 選取商品種類後的連動邏輯 (Fetch API)
async function selectCategory() {
    const category = categorySelect.value;
    if (!category) {
        // 如果沒有選擇種類，清空商品列表並重設
        resetFields();
        return;
    }

    // 重設商品列表，並顯示載入中
    productSelect.innerHTML = '<option value="" disabled selected>載入中...</option>';
    priceDisplay.textContent = '0.00'; 
    totalInput.value = 0.00;

    try {
        // 向後端 /product 路徑發送 GET 請求，帶上 category 參數
        const response = await fetch(`/product?category=${encodeURIComponent(category)}`);
        
        if (!response.ok) {
            throw new Error(`HTTP 錯誤! 狀態碼: ${response.status}`);
        }

        const data = await response.json();
        const products = data.product || []; 

        // 清空並更新商品名稱的下拉選單
        productSelect.innerHTML = '<option value="" disabled selected>請選擇商品</option>';
        products.forEach(product => {
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

// 2. 選取商品後的價格更新邏輯 (Fetch API)
async function selectProduct() {
    const product = productSelect.value;
    if (!product) {
        priceDisplay.textContent = '0.00';
        totalInput.value = 0.00;
        return;
    }

    try {
        // 向後端 /product 路徑發送 GET 請求，帶上 product 參數
        const response = await fetch(`/product?product=${encodeURIComponent(product)}`);
        
        if (!response.ok) {
            throw new Error(`HTTP 錯誤! 狀態碼: ${response.status}`);
        }

        const data = await response.json();
        const price = data.price || 0; 

        // 更新單價顯示
        // 使用 .toFixed(2) 確保價格顯示為兩位小數
        priceDisplay.textContent = parseFloat(price).toFixed(2);
        
        // 取得價格後，立即計算總價
        countTotal();

    } catch (error) {
        console.error("Fetch product price failed:", error);
        alert(`無法載入商品價格: ${error.message}`);
        priceDisplay.textContent = '0.00';
        totalInput.value = 0.00;
    }
}

// 3. 計算小計邏輯
function countTotal() {
    // 取得當前單價（從顯示元素中讀取）
    const priceText = priceDisplay.textContent;
    let price = parseFloat(priceText) || 0;

    // 取得當前數量
    let amount = parseInt(amountInput.value) || 0;

    // 確保數量不小於 1 (根據需求規格：數量必須恆大於 0)
    if (amount <= 0) {
        amount = 1;
        amountInput.value = 1;
    }

    // 計算總價 (單價 * 數量)
    const total = price * amount;
    
    // 將計算結果寫入隱藏的 product_total 欄位
    // 使用 .toFixed(2) 確保送出的資料格式正確
    totalInput.value = total.toFixed(2);
    
    // (可選) 在前端顯示總價給使用者看
    // 假設有一個元素來顯示最終總價，例如：
    // document.getElementById('total_display').textContent = total.toFixed(2);
}

// 4. 資料送出邏輯 (表單提交)
async function handleSubmit(event) {
    // 阻止表單預設的同步提交行為
    event.preventDefault(); 
    
    // 再次確保總價已計算
    countTotal(); 

    // 使用 FormData 取得所有表單欄位數據
    const formData = new FormData(orderForm);

    // 驗證必要的欄位（例如：商品名稱必須被選）
    if (!formData.get('product_name')) {
        alert('請先選擇商品名稱！');
        return;
    }
    
    // 確認狀態欄位預設為「未付款」
    if (!formData.get('product_status')) {
        formData.set('product_status', '未付款'); 
    }

    try {
        // 發送 POST 請求到後端 /product 路徑
        // 後端預期接收 form data
        const response = await fetch('/product', {
            method: 'POST',
            body: formData, // 直接傳遞 FormData
        });
        
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


// --- 綁定事件監聽器 ---

// 1. 綁定 Category 變化事件
categorySelect.addEventListener('change', selectCategory);

// 2. 綁定 Product Name 變化事件
productSelect.addEventListener('change', selectProduct);

// 3. 綁定 Amount 變化/輸入事件 (單價或數量改變都要重新計算)
amountInput.addEventListener('change', countTotal);
amountInput.addEventListener('input', countTotal); 
// 綁定一個假設存在的單價顯示元素的變化（如果它會變，這裡我們是通過 selectProduct() 來改變的，所以可以省略）

// 4. 綁定表單提交事件
if (orderForm) {
    orderForm.addEventListener('submit', handleSubmit);
}


// --- 已有輔助功能 ---

function delete_data(value) {
    // ... (您的原有邏輯)
    // 保持不變
    fetch(`/product?order_id=${value}`, {
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
        location.assign('/');     
    })
    .catch((error) => {
        console.error("發生錯誤：", error);
        alert("刪除失敗，請稍後再試");
    });
}

// 設定日期欄位預設為今天 
function setToday() {
    const today = new Date().toISOString().split("T")[0];
    const dateInput = document.getElementById("product_date");
    if (dateInput) {
        dateInput.value = today;
    }
}

// 網頁載入完成後自動設定今天日期
window.addEventListener("DOMContentLoaded", () => {
    setToday();
    // 確保所有欄位初始狀態是重設的
    resetFields(); 
});