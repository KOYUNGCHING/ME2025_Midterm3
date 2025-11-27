// 開啟與關閉Modal
function open_input_table() {
    document.getElementById("addModal").style.display = "block";
}
function close_input_table() {
    document.getElementById("addModal").style.display = "none";
}


function delete_data(value) {
    // 發送 DELETE 請求到後端 /product
    fetch(`/product?order_id=${value}`, {
        method: "DELETE",
    })
    .then((response) => {
        if (!response.ok) {
            throw new Error("伺服器回傳錯誤");
        }
        return response.json();   // 假設後端回傳 JSON 格式資料
    })
    .then((result) => {
        console.log(result);      // 在這裡處理成功的回應（例如顯示訊息）
        // 此處其實不一定需要關閉 modal，因為刪除按鈕在列表頁
        location.assign('/');     // 重新載入首頁，讓表格更新
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
});