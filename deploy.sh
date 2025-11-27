#!/bin/bash

# 專案目錄名 
PROJECT_DIR="ME2025_Midterm3" 
# 虛擬環境目錄名
VENV_DIR=".venv"
# 啟動腳本名
APP_FILE="app.py"
# 專案 Git 地址 
REPO_URL="https://github.com/KOYUNGCHING/ME2025_Midterm3.git" 

# 啟動或重啟 app.py
start_app() {
    echo "--- 啟動/重啟 ${APP_FILE} ---"
    # 嘗試殺死舊的，防止重複啟動
    pkill -f "${APP_FILE}" || true
    
    # 啟動應用，使用 nohup 讓應用在後台運行
    nohup "${VENV_DIR}/bin/python3" "${APP_FILE}" > app.log 2>&1 &
    echo "${APP_FILE} 已在後台啟動 (PID: $!)"
}

# 首次執行：Clone, 建立虛擬環境, 安裝套件, 啟動
first_run() {
    echo "--- [首次執行] 執行首次部署任務 ---"
    
    # i. clone repository
    echo "1. 正在克隆專案..."
    # 注意：git clone 會自動創建與倉庫同名的目錄
    git clone "${REPO_URL}" 
    if [ $? -ne 0 ]; then
        echo "錯誤: 專案克隆失敗！請檢查 REPO_URL 或網路連線。"
        exit 1
    fi
    cd "${PROJECT_DIR}"

    # ii. 在專案下建立虛擬環境，命命為 .venv
    echo "2. 正在建立虛擬環境 ${VENV_DIR}..."
    python3 -m venv "${VENV_DIR}"

    # iii. 自動安裝 requirements.txt 中的套件
    echo "3. 正在安裝套件..."
    source "${VENV_DIR}/bin/activate" # 啟用虛擬環境
    pip install -r requirements.txt
    deactivate # 停用虛擬環境

    # iv. 啟動 app.py
    start_app
}

# 第二次以後執行：更新, 檢查套件, 重啟 app.py
subsequent_run() {
    echo "--- [後續執行] 執行更新與重啟任務 ---"
    cd "${PROJECT_DIR}"
    
    # i. 自動更新專案版本
    echo "1. 正在更新專案版本..."
    git pull
    
    # ii. 檢查 requirements.txt 中未安裝的套件並安裝
    echo "2. 正在檢查並安裝新套件..."
    source "${VENV_DIR}/bin/activate"
    # 確保所有依賴都被滿足
    pip install -r requirements.txt
    deactivate
    
    # iii. 重啟 app.py
    start_app
}

# 檢查專案目錄是否存在，以判斷是首次執行還是後續執行
if [ ! -d "${PROJECT_DIR}" ]; then
    first_run
else
    subsequent_run
fi

echo "--- 部署腳本執行完畢 ---"