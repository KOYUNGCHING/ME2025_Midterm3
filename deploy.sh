#!/bin/bash


REPO_URL="https://example.com/your-repo.git"
TARGET_DIR="$HOME/me2025_midterm3_app"

# 如果目標資料夾已經存在，就進去做 git pull
# 否則就先 git clone 下來
if [ -d "$TARGET_DIR/.git" ]; then
    echo "目標目錄已存在，執行 git pull 更新程式碼..."
    cd "$TARGET_DIR"
    git pull
else
    echo "目標目錄不存在，執行 git clone..."
    git clone "$REPO_URL" "$TARGET_DIR"
    cd "$TARGET_DIR"
fi

# 建立或使用 .venv 虛擬環境
if [ ! -d ".venv" ]; then
    echo "建立 .venv 虛擬環境..."
    python3 -m venv .venv
fi

# 啟用虛擬環境
source .venv/bin/activate

# 安裝 requirements.txt 內的套件
if [ -f "requirements.txt" ]; then
    echo "安裝 requirements.txt 套件..."
    pip install -r requirements.txt
else
    echo "找不到 requirements.txt，略過安裝步驟。"
fi

# 啟動 Flask 應用程式
echo "啟動應用程式..."
python3 app.py